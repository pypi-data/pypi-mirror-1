#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

This is DoDoStorage.

DoDoStorage is meant as a User-Space write-once Filesystem. Much Inspiration
is drawn from MoglieFS http://www.danga.com/mogilefs/ - but it is much
simpler.

With DoDoStorage you can store files - "Documents" in DoDoStorage speak. For
each file you get an opaque "Document key" to retrive it. Stored Files are
immutable - you can't change or delete them. Every Document has an
"objecttype" whichs help to destinguish classes of Documents, a mime-type and
a timestamp. It also has a set of arbitrary attributes.

DoDoStorage is NOT POSIX Compliant -- you don't run regular Unix applications
or databases against DoDoStorage. It's meant for archiving write-once files
and doing only sequential reads. (though it might be extended to allow random
access. You can search for Meta-Data.

You will not be able to store the same byte-stream twice in a DoDoStorage. If
you store an bytestream for the second time in a DoDoStorage you will get a
reference to the first Document instead of creating a new one.

DoDoStorage provides two implementations providing nearly identical
interfaces:

backend  - This interface the actual storage engine. It is meant to have real
           filesystem access. Metadata is stored in an SQL Database. The
           backend is meant to run in a long running server process e.g.
           server.py
client   - This interface uses the RESTful interface of server.py to access
           the backend. The client does not need any local storage or database
           connections. Well suited to use over the Internet.

To use the client you need a running server process with an backend. See 
dodoserverserver for details.

You first have to initiate a StorageEngine. The constructor for the storage
engine is dependant on if you are going to use the backend, the client or the
frontend. The back needs a DB-connectionstring and a filesystem path where to
store data, the cliend needs an REST base URL and the frontend needs a REST
base URL and an db connection string.

>>> engine = dodostorage.backend.StorageEngine(connectionstring='sqlite:///test.db',
...                                            poollocation='./test')

You then can use the engine instance to add files or streams of data to the
DoDoStorage:

>>> mockfile = StringIO()
>>> mockfile.write(str(time.time())) # some testdata
>>> mockfile.seek(0)
>>> doc1 = engine.add(mockfile)
>>> doc2 = engine.add_string('same testdata, same document', mimetype='text/plain')
>>> doc3 = engine.add_string('same testdata, same document', mimetype='text/plain')
>>> doc2.key
u'49c738e44e8bce5b1571ae0f7d3578b9'


In addition you can add arbitary attributes to an document during creation and
then access these attribute like normal Python object attributes.
>>> foo = str(time.time()) # just some unique data
>>> doc = engine.add_string('test %r' % time.time(),
...                         attributes={'someattr': 'bar', 'otherattr': foo})
>>> doc.someattr
'bar'
>>> doc.otherattr == foo
True

You can retrive a document by hash (prefered) or by document id:
>>> engine.get(doc.key) == doc
True

You then can retrive lists of documents by attribute or by get a list of
recently added documents:
>>> engine.get_latest()[0] == doc
True
>>> engine.search_by_attributes(otherattr=foo)[0] == doc
True

Created by Maximillian Dornseif on 2007-06-09.
Copyright (c) 2007 HUDORA GmbH. Published under a 'BSD License'.
"""

__revision__ = "$Revision: 2009 $"

# depends on:
# huTools > r2004
# httplib2
# simplejson
# selector

import time
from StringIO import StringIO
import backend

def _test():
    """Run tests for DoDoStorage."""
    import doctest
    doctest.testmod()
    
if __name__ == '__main__':
    _test()
