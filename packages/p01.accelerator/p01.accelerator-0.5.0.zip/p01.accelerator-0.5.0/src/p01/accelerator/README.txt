======
README
======

This package offers a new browser request and publication which will catch
uploaded files and store their data in a temporary file. This persistent
temporary file can directy get used in a file storage within a zero-copy
operation (move).

The temporary file get created if the p01.cgi parser creates a file upload
from a multipart form. This persistent temporary file is observed by a special
transaction manager and will get removed after processing if the temp file path
exists at the end of the transaction. (if not moved)

The accelerator browser request applies the transaction earlier then the
default zope request. The accelerator browser request applies the transaction
manager during the request creation. This allows us to observer the file upload
and temporary file creation withhin this transaction manager. By default Zope
doesn't have a transaction manager ready at this state.

We also use a file upload processor which is much faster then the cgi
FieldStorage implementation. This gives an additional upload speedup.
For more infos about the parser, take a look at the p01.cgi package.

The uploaded file handling normaly done in a widget framework is not a part of
this package.

This package was developed as a very basic file upload handling library which
can be used as a base for any file system storage implementattion. Take a look
at p01.fsfile for such a file system storage implementation or p01.fswidget for
a ready to use implementation which offers a layer with z3c.form widgets.

Summary
-------

The p01.accelerator package offers a real boost for small or large file uploads.
The uploaded file can get consumed with a file read operation or moved to a
distributed file system storage. If you use this implementation within a file
system storage, it's recommended to take a look at p01.fsfile which provides a
persistent file system file implementation.


TMPStorage
----------

Let's test if our test temp storage is available:

  >>> import zope.component
  >>> import p01.tmp.default
  >>> import p01.tmp.interfaces

You test setup must provide a ``P01_TMP_STORAGE_PATH`` as enviroment variable.
See the test setup in buildout.cfg:

  >>> import os
  >>> 'P01_TMP_STORAGE_PATH' in os.environ
  True

As you can see in p01/tmp/default.zcml, we register our tmpStorage as an
ITMPStorage utility. Let's do this here since we do not load the default.zcml
in any configure.zcml. Note you need to load the default.zcml in you project
setup since this is an important part of how you handle accelerated tmp files:

  >>> zope.component.provideUtility(p01.tmp.default.tmpStorage)

Now we can test the ITMPStorage utility:

  >>> tmpStorage = zope.component.getUtility(p01.tmp.interfaces.ITMPStorage)
  >>> p01.tmp.interfaces.ITMPStorage.providedBy(tmpStorage)
  True

The TMPStorage path should point to the test temp storage located in parts.

  >>> tmpStorage.path
  u'.../parts/testTMPStorage'

Our storage can generate a new unused unique tmporary file path which we can
use for a new tmporary file:

  >>> tmpStorage.generateNewTMPFilePath()
  u'...parts/testTMPStorage/...'


TMPFile
-------

We can get a new empty temp file from the temp storage:

  >>> tmpFile = tmpStorage.getTMPFile()
  >>> tmpFile
  <TMPFile at ...parts/testTMPStorage/... mode='w+b'>

This file provides ITMPFile:

  >>> p01.tmp.interfaces.ITMPFile.providedBy(tmpFile)
  True

and is not closed:

  >>> tmpFile.closed
  False

and provides a path:

  >>> tmpFile.tmpPath
  u'...parts/testTMPStorage/...'

We can also check for __nonzero__:

  >>> bool(tmpFile)
  False

and provides a time stamp for creation time. Note the python doc says:
The ``ctime'' as reported by the operating system. On some systems (like Unix)
is the time of the last metadata change, and, on others (like Windows), is the
creation time (see platform documentation for details).

  >>> tmpFile.ctime is not None
  True

and provides a time stamp for last access:

  >>> tmpFile.atime is not None
  True

The TMPFile provides any method which a file object provides. Let's write
to the file:

  >>> tmpFile.write('Obama for president!')

Since we wrote data to the file, the file provides a positiv nonzero value

  >>> bool(tmpFile)
  True

Now we can close the file and open it again.

  >>> tmpFile.close()

Now the file is closed:

  >>> tmpFile.closed
  True

Now we can just read it again, we do not have to open the file again since this
is done by the read implementation itself:

  >>> tmpFile.read()
  'Obama for president!'

  >>> tmpFile.closed
  False

we can read again and it doesn't provide more data:

  >>> tmpFile.read()
  ''

but we can seek and read again:

  >>> tmpFile.seek(0)
  >>> tmpFile.read()
  'Obama for president!'

The tmp file also provides a size:

  >>> tmpFile.size
  20

or a lenght:

  >>> len(tmpFile)
  20
