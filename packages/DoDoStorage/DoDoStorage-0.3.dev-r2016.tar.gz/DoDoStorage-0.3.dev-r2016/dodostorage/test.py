#!/usr/bin/env python
# encoding: utf-8
"""
test.py - UnitTests for DoDoStorage.

The client.py related tests need a running server to work. So try:
PYTHONPATH=. python dodostorage/dodoserver  --port=8000 --host=0.0.0.0
before running these tests.

Also be sure, to remove the test database (test.db) after running the tests, because stale data in the test
DB can screw up the results.

Created by Maximillian Dornseif on 2007-06-09.
Copyright (c) 2007 HUDORA GmbH. Published under a 'BSD License'.
"""

import unittest, os, datetime, time
from dodostorage import backend, client

__revision__ = "$Revision: 2016 $"

class TestBackend(unittest.TestCase):
    """Test the functionality in backend.py."""
    
    def setUp(self):
        self.engine = backend.StorageEngine(serverurl='http://127.0.0.1:8000/',
                      connectionstring='sqlite:///teststore.db', poollocation='./teststorepools')
    
    
    def tearDown(self):
        os.unlink('teststore.db')
        for root, dirs, files in os.walk('./teststorepools', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.removedirs('./teststorepools')
    
    
    def test_add_file(self):
        """Ensure that adding file-like objects works."""
        doc1 = self.engine.add_file('dodostorage/__init__.py')
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1.file.read(), open('dodostorage/__init__.py').read())
    
    
    def test_add(self):
        """Ensure that adding bytestreams works."""
        doc1 = self.engine.add('longnow!')
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1.file.read(), 'longnow!')
    
    
    def test_category(self):
        """Ensure that adding bytestreams works."""
        doc1 = self.engine.add('longnow!', 'testcat')
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1.category, 'testcat')
        self.assertEqual(doc2.category, 'testcat')
    
    
    def test_add_timestamp(self):
        """Ensure that we handle document_timestamp."""
        doc1 = self.engine.add(str(time.time()), document_timestamp=datetime.datetime(2007, 3, 4, 5, 6, 7))
        self.assertEqual(doc1.document_timestamp, datetime.datetime(2007, 3, 4, 5, 6, 7))
    
    
    def test_add_dupes(self):
        """Ensure that dublicate data added does not incerase filecount and bytecount."""
        doc1 = self.engine.add('longnow!')
        filecount, bytecount = doc1.storagepool.filecount, doc1.storagepool.bytecount
        doc2 = self.engine.add('longnow!')
        self.assertEqual(doc1.storagepool.filecount, doc2.storagepool.filecount)
        self.assertEqual(filecount, doc2.storagepool.filecount)
        self.assertEqual(bytecount, doc2.storagepool.bytecount)
    
    
    def test_add_attributes(self):
        doc1 = self.engine.add('longnow!', attributes=dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8))
        self.assertEqual(doc1.a, '1')
        self.assertEqual(doc1.b, '2')
        self.engine.session.clear()
        doc2 = self.engine.get(doc1.key)
        doc2.update_attributes()
        self.assertEqual(doc2.a, '1')
    
    
    def test_add_dupe_attributes(self):
        doc1 = self.engine.add('longnow!')
        doc2 = self.engine.add('longnow!', attributes=dict(a=1))
        self.assertEqual(doc2.a, '1')
        doc2 = self.engine.add('longnow!', attributes=dict(b=2))
        self.assertEqual(doc2.a, '1')
        self.assertEqual(doc2.b, '2')
    
    
    def test_add_attribute_dupes(self):
        doc1 = self.engine.add('longnow!', attributes=dict(x=1))
        doc2 = self.engine.add('longnow!', attributes=dict(x=1))
        doc3 = self.engine.add('longnow!', attributes=dict(x=2))
        doc3 = self.engine.add('longnow!', attributes=dict(y=3))
        self.assertEqual(doc1.x, '1')
        self.assertEqual(len(doc1.attributes), 2)
        self.assertEqual(doc3.x, '1')
        self.assertEqual(len(doc3.attributes), 2)
    
    
    def test_get(self):
        doc1 = self.engine.add('longnow!', 'TestBild')
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1, doc2)
        self.assertEqual(doc1.file.read(), 'longnow!')
        self.assertEqual(doc2.file.read(), 'longnow!')
    
    
    def test_get_content(self):
        doc = self.engine.add('longnow!', 'TestBild')
        data = self.engine.get_content(doc.key)
        self.assertEqual(data, 'longnow!')
    
    
    def test_doc_file(self):
        doc = self.engine.add('longnow!', 'TestBild')
        self.assertTrue(hasattr(doc.file, 'read'))
        self.assertEqual(''.join(list(doc.data)), 'longnow!')
    
    
    def test_doc_data(self):
        doc = self.engine.add('longnow!', 'TestBild')
        self.assertTrue(hasattr(doc.data, '__iter__'))
        self.assertEqual(''.join(list(doc.data)), 'longnow!')
    
    
    def test_doc_len(self):
        doc = self.engine.add('longnow!', 'TestBild')
        self.assertEqual(len(doc), len('longnow!'))
    
    
    def test_doc_link(self):
        doc1 = self.engine.add('longnow!', 'TestBild')
        doc2 = self.engine.add('longnow!', 'TestBild')
        self.assertEqual(doc1.link, doc2.link)
        self.assertEqual(doc1.link[:7], 'http://')
    
    
    def test_bytecount(self):
        doc = self.engine.add('longnow!', 'TestBild')
        bytecount = doc.storagepool.bytecount
        doc = self.engine.add('bighere', 'TestBild')
        self.assertEqual(doc.storagepool.bytecount, bytecount + len('bighere'))
    
    
    def test_filecount(self):
        doc = self.engine.add('longnow!', 'TestBild')
        filecount = doc.storagepool.filecount
        doc = self.engine.add('bighere', 'TestBild')
        self.assertEqual(doc.storagepool.filecount, filecount + 1)
    
    
    def test_get_latest(self):
        doc1 = self.engine.add('longnow!', 'TestBild')
        doc2 = self.engine.add('bighere', 'TestBild')
        latest = self.engine.get_latest(limit=1)
        self.assertEqual(len(latest), 1)
        self.assertEqual(latest, [doc2])
        latest = self.engine.get_latest()
        self.assertEqual(len(latest), 2)
    
    
    def test_search_by_attributes(self):
        doc1 = self.engine.add('longnow!', 'TestBild', attributes=dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7))
        doc2 = self.engine.add('bighere', 'TestBild', attributes=dict(a=1, b=1, c=1, d=1, e=1, f=1, g=1))
        self.engine.session.clear()
        results = self.engine.search_by_attributes(a='2')
        self.assertEqual(len(results), 0)
        results = self.engine.search_by_attributes(a='1')
        self.assertEqual(len(results), 2)
        results = self.engine.search_by_attributes(b='2')
        self.assertEqual(len(results), 1)
    
    
    def test_get_categories(self):
        doc1 = self.engine.add('longnow!', 'TestBild')
        results = self.engine.get_categories()
        self.assertEqual(results, ['TestBild'])
    
    
    def test_get_attributes(self):
        doc1 = self.engine.add('longnow!', 'TestBild', attributes=dict(a=1, b=2, c=3))
        results = sorted(self.engine.get_attributes())
        self.assertEqual(results, ['a', 'b', 'c'])
    

class TestClient(unittest.TestCase):
    """Test the functionality in client.py."""
    # TODO: these tests at the moment assume you have a running server. This can be done more clever.
    # see: http://bitworking.org/news/172/Test-stubbing-httplib2
    
    def setUp(self):
        self.engine = client.StorageEngine(serverurl='http://127.0.0.1:8000/')
    
    
    def test_add_file(self):
        """Ensure that adding file-like objects works."""
        doc1 = self.engine.add_file('dodostorage/__init__.py')
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1.file.read(), open('dodostorage/__init__.py').read())
    
    
    def test_add(self):
        """Ensure that adding bytestreams works."""
        doc1 = self.engine.add('longnow!')
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1.file.read(), 'longnow!')
        self.assertEqual(doc2.file.read(), 'longnow!')
    
    
    def test_category(self):
        """Ensure that adding bytestreams works."""
        catname = 'testcat-%f' % time.time()
        doc1 = self.engine.add('longnow:%f' % time.time(), category=catname)
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1.category, catname)
        self.assertEqual(doc2.category, catname)
        doc1 = self.engine.add('bighere:%f' % time.time(), catname)
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1.category, catname)
        self.assertEqual(doc2.category, catname)
    
    
    def test_add_timestamp(self):
        """Ensure that we handle document_timestamp."""
        doc1 = self.engine.add(str(time.time()), document_timestamp=datetime.datetime(2007, 3, 4, 5, 6, 7))
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1.document_timestamp, datetime.datetime(2007, 3, 4, 5, 6, 7))
        self.assertEqual(doc2.document_timestamp, datetime.datetime(2007, 3, 4, 5, 6, 7))
    
    
    def test_add_dupeattributes(self):
        doc1 = self.engine.add('longnow!')
        doc2 = self.engine.add('longnow!', attributes=dict(a=1))
        self.assertEqual(doc2.a, '1')
        doc2 = self.engine.add('longnow!', attributes=dict(b=2))
        self.assertEqual(doc2.b, '2')
    
    
    def test_get(self):
        doc1 = self.engine.add('longnow!', 'TestBild')
        doc2 = self.engine.get(doc1.key)
        self.assertEqual(doc1.key, doc2.key)
        self.assertEqual(doc1.file.read(), 'longnow!')
        self.assertEqual(doc2.file.read(), 'longnow!')
    
    
    def test_get_content(self):
        doc = self.engine.add('longnow!', 'TestBild')
        data = self.engine.get_content(doc.key)
        self.assertEqual(data, 'longnow!')
    
    
    def test_doc_file(self):
        doc = self.engine.add('longnow!', 'TestBild')
        self.assertTrue(hasattr(doc.file, 'read'))
        self.assertEqual(''.join(list(doc.data)), 'longnow!')
    
    
    def test_doc_data(self):
        doc = self.engine.add('longnow!', 'TestBild')
        self.assertTrue(hasattr(doc.data, '__iter__'))
        self.assertEqual(''.join(list(doc.data)), 'longnow!')
    
    
    def test_doc_len(self):
        doc = self.engine.add('longnow!', 'TestBild')
        self.assertEqual(len(doc), len('longnow!'))
    
    
    def test_doc_link(self):
        doc1 = self.engine.add('longnow!', 'TestBild')
        doc2 = self.engine.add('longnow!', 'TestBild')
        self.assertEqual(doc1.link, doc2.link)
        self.assertEqual(doc1.link[:7], 'http://')
    
    
    def test_get_latest(self):
        doc1 = self.engine.add('longnow:%f' % time.time(), 'TestBild')
        doc2 = self.engine.add('bighere:%f' % time.time(), 'TestBild')
        latest = self.engine.get_latest(limit=1)
        self.assertEqual(len(latest), 1)
        self.assertEqual(latest[0].key, doc2.key)
        list(latest[0].data)
        latest = self.engine.get_latest(limit=2)
        self.assertEqual(len(latest), 2)
    
    
    def test_search_by_attributes(self):
        doc1 = self.engine.add('longnow!', 'TestBild', attributes=dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7))
        doc2 = self.engine.add('bighere', 'TestBild', attributes=dict(a=1, b=1, c=1, d=1, e=1, f=1, g=1))
        results = self.engine.search_by_attributes(a='2')
        self.assertEqual(len(results), 0)
        results = self.engine.search_by_attributes(a='1')
        self.assertEqual(len(results), 2)
        results = self.engine.search_by_attributes(b='2')
        self.assertEqual(len(results), 1)
    
    
    def test_get_categories(self):
        catname = 'testcat-%f' % time.time()
        doc1 = self.engine.add('longnow:%f' % time.time(), catname)
        results = self.engine.get_categories()
        self.assertEqual(results, [catname])
    
    
    def test_get_attributes(self):
        self.engine.add('longnow!', 'TestBild', attributes=dict(a=1, b=2, c=3))
        results = sorted(self.engine.get_attributes())
        self.assertTrue('a' in results)
        self.assertTrue('b' in results)
        self.assertTrue('c' in results)
    


def _test():
    """Run tests for DoDoStore."""
    unittest.main()
    

if __name__ == '__main__':
    _test()

