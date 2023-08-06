======
README
======

This package offers a temporary file storage and a temporary file
implementation. The temporary file provides a path to a file system file which
is persistent and doesn't get removed by itself like a temp file does by
default. This allows us to use the file system file hold by the tmp file with
zero-copy operations in other implementations.

The tmp file is observed by a transaction. This transaction will remove files
on transaction abort or if they exist at the end of the transacction. This means
a file system file must get moved to a new location and the tmpPath of our tmp
file implementation must set to None. Otherwise the file system file get
removed by the transaction.


TMPStorage
----------

Let's test if our test temp storage is available:

  >>> import zope.component
  >>> from p01.tmp import interfaces

As you can see in default.zcml, we register our tmpStorage as an ITMPStorage
utility. Let's do this here since we do not load the default.zcml for this test:

  >>> from p01.tmp import default
  >>> zope.component.provideUtility(default.tmpStorage)

Now we can test the ITMPStorage utility:

  >>> tmpStorage = zope.component.getUtility(interfaces.ITMPStorage)
  >>> interfaces.ITMPStorage.providedBy(tmpStorage)
  True

The TMPStorage path should point to the test temp storage located in parts.

  >>> tmpStorage.path
  u'.../parts/testTMPStorage'

Our storage can generate a new unused unique tmporary file path which we can
use for a new tmporary file:

  >>> tmpStorage.generateNewTMPFilePath()
  u'...parts/testTMPStorage/...-...-...-...-...'


TMPFile
-------

We can get a new empty temp file from the temp storage:

  >>> tmpFile = tmpStorage.getTMPFile()

The mode 'w+b' is very important!

  >>> tmpFile
  <TMPFile at ...parts/testTMPStorage/... mode='w+b'>

This file provides ITMPFile:

  >>> interfaces.ITMPFile.providedBy(tmpFile)
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

or a length:

  >>> len(tmpFile)
  20

and the current position:

  >>> tmpFile.tell()
  20L

A you can see a file contains a mode in it's representation if we have an open
file. A closed file doesn't provide a mode:

  >>> tmpFile
  <TMPFile at ...parts/testTMPStorage/... mode='r+b'>
  >>> 'mode' in tmpFile.__repr__()
  True

  >>> tmpFile.close()
  >>> 'mode' in tmpFile.__repr__()
  False

The closed tmp file still has a size:

  >>> tmpFile.size
  20

or a length:

  >>> len(tmpFile)
  20

current position is already gone:

  >>> tmpFile.tell()
  0


We can kill the TMPFile:

  >>> tmpFile.release()

It will loose the filename:

  >>> tmpFile.tmpPath is None
  True

A closed file has 0 size:

  >>> tmpFile.size
  0

or length:

  >>> len(tmpFile)
  0

current position is gone:

  >>> tmpFile.tell()
  0


Transactional behavour
----------------------

As written earlier, the TMPFile should go away on transaction boundaries.
Let's test this.

  >>> import transaction
  >>> import os.path

First kill of all transactions:

  >>> transaction.abort()

Create a new TMPFile:

  >>> tmpFile = tmpStorage.getTMPFile()
  >>> tmpFile.write('foobar')

Get hold of the filename:

  >>> fname = tmpFile.tmpPath

TMPFile has to exist on the filesystem:

  >>> os.path.exists(fname)
  True

Now if we commit the transaction the file must be gone:

  >>> transaction.commit()
  >>> os.path.exists(fname)
  False

  >>> tmpFile.tmpPath is None
  True


Same story, but we'll now abort the transaction:

  >>> tmpFile = tmpStorage.getTMPFile()
  >>> tmpFile.write('foobar')

  >>> fname = tmpFile.tmpPath

  >>> os.path.exists(fname)
  True

  >>> transaction.abort()
  >>> os.path.exists(fname)
  False


Even more interesting story, we'll make a transaction fail.

Install out datamanager that will fail it:

  >>> from p01.tmp.tests import FailingDataManager
  >>> tm = transaction.manager
  >>> dm = FailingDataManager(tm)
  >>> tm.get().join(dm)

Create the TMPFile:

  >>> tmpFile = tmpStorage.getTMPFile()
  >>> tmpFile.write('foobar')

  >>> fname = tmpFile.tmpPath

  >>> os.path.exists(fname)
  True

Commit the transaction... it fails, but we wanted that!

  >>> transaction.commit()
  Traceback (most recent call last):
  ...
  ValueError: commit

The TMPFile is gone:

  >>> os.path.exists(fname)
  False

We need to abort(?)

  >>> transaction.abort()


Same story, but with abort now:

  >>> from p01.tmp.tests import FailingDataManager
  >>> tm = transaction.manager
  >>> dm = FailingDataManager(tm, 'abort')
  >>> tm.get().join(dm)

Create the TMPFile:

  >>> tmpFile = tmpStorage.getTMPFile()
  >>> tmpFile.write('foobar')

  >>> fname = tmpFile.tmpPath

  >>> os.path.exists(fname)
  True

Commit the transaction... it fails, but we wanted that!

  >>> transaction.abort()
  Traceback (most recent call last):
  ...
  ValueError: abort

The TMPFile is gone:

  >>> os.path.exists(fname)
  False


Adapting to ITMPFile
--------------------

A comfortable way to get a new TMPFile is to adapt something to it:

  >>> interfaces.ITMPFile(None)
  Traceback (most recent call last):
  ...
  TypeError: ('Could not adapt', None, <InterfaceClass p01.tmp.interfaces.ITMPFile>)

Ops, we forgot register the adapter:

  >>> from p01.tmp import file
  >>> import zope.component
  >>> zope.component.provideAdapter(file.getTMPFile)

Try again:

  >>> interfaces.ITMPFile(None)
  <TMPFile at .../testTMPStorage/... mode='w+b'>

Luckily we provided the ITMPStorage utility at the beginning so we got a result.

Edge case
---------

p01.cgi uses the tempfile in the following manner:
- creates it
- writes to it
- seeks to 0
- reads from it
NOTE: the tempfile is NOT closed between the write and read!
(if I remember well closing a python tempfile makes it go away)

Let's simulate the above:

Create the file:

  >>> tmpFile = tmpStorage.getTMPFile()

Write to it:

  >>> tmpFile.write('Congratulations Mr. President')

Seek to 0

  >>> tmpFile.seek(0)

Read from it:

  >>> tmpFile.read()
  'Congratulations Mr. President'
