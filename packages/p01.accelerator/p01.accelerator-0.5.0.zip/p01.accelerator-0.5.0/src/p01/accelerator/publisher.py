##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

from StringIO import StringIO
from tempfile import TemporaryFile
from types import StringType

import transaction
import zope.interface
import zope.component
from zope.publisher.browser import BrowserRequest
from zope.security.management import newInteraction
from zope.publisher.browser import get_converter
from zope.publisher.browser import CONVERTED
from zope.publisher.browser import SEQUENCE
from zope.publisher.browser import DEFAULT
from zope.publisher.browser import RECORD
from zope.publisher.browser import RECORDS

import zope.app.security.interfaces
from zope.app.publication.interfaces import IBrowserRequestFactory

import p01.cgi.interfaces
import p01.cgi.parser
import p01.tmp.interfaces
from p01.accelerator import interfaces


# TODO: implement size and zope.conf hook
class HTTPInputStream(object):
    """Special stream that supports caching the read data.

    This is important, so that we can retry requests.
    """
    def __init__(self, stream, environment):
        self.stream = stream
        size = environment.get('CONTENT_LENGTH')
        # There can be no size in the environment (None) or the size
        # can be an empty string, in which case we treat it as absent.
        if not size:
            size = environment.get('HTTP_CONTENT_LENGTH')
        if not size or int(size) < 65536:
            self.cacheStream = StringIO()
        else:
            self.cacheStream = TemporaryFile()
        self.size = size and int(size) or -1

    def getCacheStream(self):
        self.read(self.size)
        self.cacheStream.seek(0)
        return self.cacheStream

    def read(self, size=-1):
        data = self.stream.read(size)
        self.cacheStream.write(data)
        return data

    def readline(self, size=None):
        if size is not None:
            data = self.stream.readline(size)
        else:
            data = self.stream.readline()
        self.cacheStream.write(data)
        return data

    def readlines(self, hint=0):
        data = self.stream.readlines(hint)
        self.cacheStream.write(''.join(data))
        return data


# TODO: check if we can use the TMPFile directly if we implement a headers
#       attribute, bad idea?
class TMPFileUpload(object):
    """File upload objects

    File upload objects are used to represent file-uploaded data.

    File upload objects can be used just like files.

    In addition, they have a 'headers' attribute that is a dictionary
    containing the file-upload headers, and a 'filename' attribute
    containing the name of the uploaded file.
    """

    def __init__(self, aFieldStorage):

        file = aFieldStorage.file
        # first close the file for all future processing
        file .close()
        self.tmpFile = file

        if hasattr(file, '__methods__'):
            methods = file.__methods__
        else:
            methods = ['close', 'fileno', 'flush', 'isatty',
                'read', 'readline', 'readlines', 'seek',
                'tell', 'truncate', 'write', 'writelines',
                'name']

        for m in methods:
            if hasattr(file, m):
                self.__dict__[m] = getattr(file, m)

        self.headers = aFieldStorage.headers
        self.filename = unicode(aFieldStorage.filename, 'UTF-8')


class AcceleratorBrowserRequest(BrowserRequest):
    """Can handle very large and fast file upload.

    We use persistent files implemented as TMPFile not temporary files and
    extract the upload data directly to this files. Later we move this files
    to it's new location if we use a file system file storage or we consume the
    data if we store the content in the ZODB.

    Another improvment is the parseFormData method which replaces the default
    cgi.FieldStorage. This parser implementation fixes some issues in the
    original implementation like:

    - reads the full file data into memory in FieldStorage.__repr__ method

    Note, we already started the transaction in the setPublication method.
    Normaly this is done in the publications beforeTravers method. This allows
    us to observe the upload file within the transaction manager and remove
    them on errors.

    """

    zope.interface.implements(interfaces.IAcceleratorBrowserRequest)
    zope.interface.classProvides(IBrowserRequestFactory)

    def __init__(self, body_instream, environ, response=None):
        super(AcceleratorBrowserRequest, self).__init__(body_instream, environ,
            response)
        self._body_instream = HTTPInputStream(body_instream, self._orig_env)

    def setPublication(self, pub):
        if not interfaces.IAcceleratorBrowserPublication.providedBy(pub):
            # Avoid to apply a wrong publication. This could happen because the
            # BrowserPublication is hard coded in some places e.g. Debugger
            pub = AcceleratorBrowserPublication(pub.db)
        super(AcceleratorBrowserRequest, self).setPublication(pub)

        # Try to authenticate against the root authentication utility.
        auth = zope.component.getGlobalSiteManager().getUtility(
            zope.app.security.interfaces.IAuthentication)
        principal = auth.authenticate(self)
        if principal is None:
            principal = auth.unauthenticatedPrincipal()
            if principal is None:
                # Get the fallback unauthenticated principal
                principal = zope.component.getUtility(
                    zope.app.security.interfaces.IFallbackUnauthenticatedPrincipal)

        # start new transaction
        self.setPrincipal(principal)
        newInteraction(self)
        transaction.begin()

    def getTMPFileFactory(self):
        return p01.tmp.interfaces.ITMPFile(self)

    def processInputs(self):
        'See IPublisherRequest'
        fp = None
        if self.method != 'GET':
            # Process self.form if not a GET request.
            fp = self._body_instream

        # parse form data and use our built in tmp file factory
        fslist = p01.cgi.parser.parseFormData(self.method, inputStream=fp,
            environ=self._environ, tmpFileFactory=self.getTMPFileFactory)
        if fslist is not None:
            self._BrowserRequest__meth = None
            self._BrowserRequest__tuple_items = {}
            self._BrowserRequest__defaults = {}

            # process all entries in the field storage (form)
            for item in fslist:
                self.__processItem(item)

            if self._BrowserRequest__defaults:
                self._BrowserRequest__insertDefaults()

            if self._BrowserRequest__tuple_items:
                self._BrowserRequest__convertToTuples()

            if self._BrowserRequest__meth:
                self.setPathSuffix((self._BrowserRequest__meth,))

    def __processItem(self, item):
        """Process item in the field storage and use TMPFileUpload."""

        # Note: A field exists for files, even if no filename was
        # passed in and no data was uploaded. Therefore we can only
        # tell by the empty filename that no upload was made.
        key = item.name
        if p01.cgi.interfaces.IMultiPartField.providedBy(item) \
            and item.file is not None and \
            (item.filename is not None and item.filename != ''):
            item = TMPFileUpload(item)
        else:
            item = item.value

        flags = 0
        converter = None

        # Loop through the different types and set
        # the appropriate flags
        # Syntax: var_name:type_name

        # We'll search from the back to the front.
        # We'll do the search in two steps.  First, we'll
        # do a string search, and then we'll check it with
        # a re search.
        while key:
            pos = key.rfind(":")
            if pos < 0:
                break
            match = self._typeFormat.match(key, pos + 1)
            if match is None:
                break

            key, type_name = key[:pos], key[pos + 1:]

            # find the right type converter
            c = get_converter(type_name, None)

            if c is not None:
                converter = c
                flags |= CONVERTED
            elif type_name == 'list':
                flags |= SEQUENCE
            elif type_name == 'tuple':
                self._BrowserRequest__tuple_items[key] = 1
                flags |= SEQUENCE
            elif (type_name == 'method' or type_name == 'action'):
                if key:
                    self._BrowserRequest__meth = key
                else:
                    self._BrowserRequest__meth = item
            elif (type_name == 'default_method'
                    or type_name == 'default_action') and \
                    not self._BrowserRequest__meth:
                if key:
                    self._BrowserRequest__meth = key
                else:
                    self._BrowserRequest__meth = item
            elif type_name == 'default':
                flags |= DEFAULT
            elif type_name == 'record':
                flags |= RECORD
            elif type_name == 'records':
                flags |= RECORDS
            elif type_name == 'ignore_empty' and not item:
                # skip over empty fields
                return

        # Make it unicode if not None
        if key is not None:
            key = self._decode(key)

        if type(item) == StringType:
            item = self._decode(item)

        if flags:
            self._BrowserRequest__setItemWithType(key, item, flags, converter)
        else:
            self._BrowserRequest__setItemWithoutType(key, item)
