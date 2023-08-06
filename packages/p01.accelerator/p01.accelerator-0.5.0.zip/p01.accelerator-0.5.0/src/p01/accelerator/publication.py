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

import zope.interface
import zope.component

from zope.app.publication.interfaces import IRequestPublicationFactory
from zope.app.publication.interfaces import IBrowserRequestFactory
from zope.app.publication.browser import BrowserPublication

from p01.accelerator import interfaces
from p01.accelerator import publisher


class AcceleratorBrowserPublication(BrowserPublication):
    """Accelerator browser publication
    
    The BrowserPublication which inherits ZopePublication will start the
    transaction in the beforeTraversal method. Since we apply our transaction
    earlier then the ZopePublication does, we nned to skipthis transaction
    creation.
    
    We start our transaction during the createion of the request which allows 
    us to observer the file upload within a temporary file upload transaction 
    manager.

    """

    zope.interface.implements(interfaces.IAcceleratorBrowserPublication)

    def beforeTraversal(self, request):
        pass


class AcceleratorBrowserFactory(object):
    """Special Accelerator browser request factory which returns the right 
    publication
    """

    zope.interface.implements(IRequestPublicationFactory)

    def canHandle(self, environment):
        return True

    def __call__(self):
        # hook wihich allows to register a custom IBrowserRequestFactory
        request_class = zope.component.queryUtility(
                IBrowserRequestFactory,
                default=publisher.AcceleratorBrowserRequest)
        return request_class, AcceleratorBrowserPublication
