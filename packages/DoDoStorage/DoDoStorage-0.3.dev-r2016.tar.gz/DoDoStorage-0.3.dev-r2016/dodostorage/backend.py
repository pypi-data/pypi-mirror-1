#!/usr/bin/env python
# encoding: utf-8
"""
backend.py - This implements the actual on disk storage of the DoDoStorage system and implements all 
database schemata.

Created by Maximillian Dornseif on 2007-06-09.
Copyright (c) 2007 HUDORA GmbH. Published under a 'BSD License'.
"""

import os, os.path, mimetypes, sha, md5, logging, datetime, re
from types import StringType, UnicodeType
from StringIO import StringIO
import sqlalchemy
from sqlalchemy import func, mapper, relation, create_engine, and_, desc
from sqlalchemy import DynamicMetaData, PassiveDefault, ForeignKey
from sqlalchemy import Column, Table, Integer, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm.mapper import global_extensions
from sqlalchemy.ext.sessioncontext import SessionContext
from huTools.luids import luid

__revision__ = "$Revision: 2016 $"

LOG = logging

context = SessionContext(sqlalchemy.create_session)
global_extensions.append(context.mapper_extension)

metadata = DynamicMetaData()

# from shutil.py with added hashing
def copyfileobj(fsrc, fdst, length=16*1024):
    """Copy data from file-like object fsrc to file-like object fast and returns (md5, sha1) of that file."""

    filehash1 = md5.new()
    filehash2 = sha.new()
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        filehash1.update(buf)
        filehash2.update(buf)
        fdst.write(buf)
    return filehash1.hexdigest(), filehash2.hexdigest()

extensionmapping = {'text/plain':               '.txt',
                    'text/x-python':            '.py',
                    'image/png':                '.png',
                    'image/gif':                '.gif',
                    'application/octet-stream': '.bin',
                    }
def guess_extension(content_type):
    """Guess the prefered extension for an content-type.
    
    Hopfully smarter than Pythons's original mimetypes.guess_extension()."""
    
    if content_type not in extensionmapping:
        print "warning: unknown content-type %r" % content_type
    return extensionmapping.get(content_type, mimetypes.guess_extension(content_type, strict=False))


class StoragePool(object):
    """StoragePools hold Documents."""
    
    def __init__(self, path, url):
        self.path = path
        self.url = url
        # placeholders for database-filled attributes
        self.documents = None
        self.filecount = None
        self.bytecount = None
        self.documents = None
    
    def _get_link(self):
        """Returns the link base for files stored in this StoragePool."""
        return self.url
    link = property(_get_link)
    
    
    def store(self, newdoc, originalfile):
        """Phisically store a Document/File in the storage pool.
        
        Duplicates are merged into one Document."""
        
        filepath = []
        if not (hasattr(newdoc, 'content_type') and newdoc.content_type) \
           and (type(originalfile) in (StringType, UnicodeType)):
            newdoc.content_type, encoding = mimetypes.guess_type(originalfile, strict=False)
        
        if not hasattr(originalfile, 'read'):
            # we assume, this is not a file object fut a pathname, so open it
            filename =  os.path.basename(originalfile)
            originalfile = open(originalfile, 'rb')
        
        tmpstoragepath = os.path.join(self.path, '%s.tmp' % luid())
        # ensure directory exists
        if not os.path.exists(os.path.dirname(tmpstoragepath)):
            os.makedirs(os.path.dirname(tmpstoragepath))
        storagefile = open(tmpstoragepath, 'wb')
        newdoc.md5, newdoc.sha1 = copyfileobj(originalfile, storagefile)
        storagefile.close() # flush outfile
        
        # check if we have an dublicate
        samekey = self.session.query(Document).select(document_table.c.md5==newdoc.key)
        if len(samekey) > 0:
            samekey = samekey[0]
            # whe have an dublicate - delete the newly created file and return the old file with the same key
            LOG.info('%s is a dublicate of %s - deleting %r' % (newdoc, samekey, tmpstoragepath))
            samekey.update_attributes()
            if samekey.key == newdoc.key and samekey.sha1 != newdoc.sha1:
                # we found an MD5 collision
                raise RuntimeError, "An md collision! %s|%s|%s|%s|%s" % (samekey.key, newdoc.key,
                                                                         samekey.sha1, newdoc.sha1,
                                                                         tmpstoragepath)
            # add attributes from new document to existing document (samekey)
            for attribute in newdoc.attributes:
                if not hasattr(samekey, attribute.name):
                    # this attribute doesn't exist so far.
                    attr = DocumentAttribute()
                    attr.name = attribute.name
                    attr.value = attribute.value
                    samekey.attributes.append(attr)
                    setattr(samekey, attribute.name, attribute.value)
                elif getattr(samekey, attribute.name) != attribute.value:
                    LOG.info('trying to change attribute %r on %s from %r to %r.' % (attribute.name, samekey,
                                                          getattr(samekey, attribute.name), attribute.value))
            # clean junk left over from newdoc
            if os.path.exists(samekey.get_filepath()):
                os.unlink(tmpstoragepath)
            else:
                os.rename(tmpstoragepath, samekey.get_filepath())
            self.session.delete(newdoc)
            self.session.flush()
            return samekey
        
        self.documents.append(newdoc)
        newdoc.storagepool = self
        self.session.flush() #  ensure newdoc has an ID
        filepath.insert(0, '%04x' % newdoc.id)
        newdoc.path = '-'.join(filepath)
        
        if newdoc.content_type:
            mimeext = guess_extension(newdoc.content_type)
            if not newdoc.path.endswith(mimeext):
                newdoc.path = newdoc.path + mimeext
        
        os.rename(tmpstoragepath, os.path.join(self.path, newdoc.path))
        
        LOG.debug('storing %s (%r)' % (newdoc, os.path.join(self.path, newdoc.path)))
        
        self.filecount += 1
        self.bytecount += os.path.getsize(os.path.join(self.path, newdoc.path))
        self.documents.append(newdoc)
        self.session.flush()
        return newdoc
        
    
class Document(object):
    """Represents a Document in DoDoStorage."""
    
    #def __init__(self):
        # placeholders for database-filled attributes
        # self.storagepool = None
        # self.path = None
        # self.md5 = None
        # self.id = None
        # self.category = None
        # self.document_timestamp = None
        # self.content_type = None
        # self.attributes = [None]
    
    
    def get_filepath(self):
        """Return the file associated with a document as an Python file Object."""
        return os.path.join(self.storagepool.path, self.path)
    
    
    def _get_file(self):
        """Return the file associated with a document as an Python file Object."""
        return open(self.get_filepath(), 'rb')
    file = property(_get_file)
    
    
    def _get_data(self):
        """Return an iterable representing the data stored in a document."""
        # files are iterables
        return open(self.get_filepath(), 'rb')
    data = property(_get_data)
    
    
    def _get_link(self):
        """Return an URI where this Document/File can be accessed."""
        return (u'%sdocument/%s/' % (self.storagepool.link, self.key)).encode('iso-8859-1')
    link = property(_get_link)
    
    
    def _get_key(self):
        """Return the key to access this Document."""
        return self.md5
    key = property(_get_key)
    
    
    def update_attributes(self):
        """Takes the attributes array and convert is to actual object attributes."""
        for attr in self.attributes:
            setattr(self, attr.name, str(attr.value))
    
    
    def __len__(self):
        return os.path.getsize(self.get_filepath())
    
    
    def __str__(self):
        if self.document_timestamp:
            return "Document %s (%s)" % (self.id, self.document_timestamp.strftime('%Y-%m-%d'))
        return "Document %s" % (self.id,)
    

class DocumentAttribute(object):
    """Represent a Document's Attributes."""
    
    # def __init__(self):
    #     # placeholders for database-filled attributes
    #     self.document = None
    #     self.name = None
    #     self.value = None
    
    
    def _get_link(self):
        """Get the link where Dokuments with this attributes can be found."""
        
        return (u'%sdocuments/search/%s/%s/' % (self.document.storagepool.link,
                                                self.name, self.value)).encode('iso-8859-1')
    link = property(_get_link)
    
    
    def __repr__(self):
        return "DocumentAttribute(%s, %s:%s)" % (self.document, self.name, self.value)
    
    

class StorageEngine(object):
    """StorageEngine stores and retrives Documents into andfrom StoragePools."""
    
    def __init__(self, serverurl, connectionstring='sqlite:///teststore.db', poollocation='./teststorepools'):
        super(StorageEngine, self).__init__()
        self.serverurl = serverurl
        # Create database connection.
        engine = create_engine(connectionstring, pool_recycle=3600) #, echo=True)
        metadata.connect(engine)
        metadata.create_all()
        self.session = context.current
        if self.session.query(StoragePool).count() < 1:
            self.storagepool = StoragePool(os.path.join(poollocation, 'testpool/'), serverurl)
            self.session.save(self.storagepool)
            self.session.flush()
        else:
            self.storagepool = self.session.query(StoragePool).select()[0]
        self.storagepool.session = self.session
    
    def _cleankey(self, key):
        """Clean up a document key so it contains only characters valid in a document.key"""
        return re.sub('[^a-zA-Z0-9_-]', ' ', key)
    
    
    def add_file(self, sourcefile, category='unknown', attributes={}, document_timestamp=None,
                 content_type=None):
        """Store a file.
        
        sourcefile may be a path or an open file object."""
        
        newdoc = Document()
        for key, value in attributes.items():
            attr = DocumentAttribute()
            attr.name = key
            attr.value = str(value)
            newdoc.attributes.append(attr)
            setattr(newdoc, key, str(value))
        newdoc.category = category
        if document_timestamp:
            newdoc.document_timestamp = document_timestamp
        else:
            newdoc.document_timestamp = datetime.datetime.utcnow()
        if content_type:
            newdoc.content_type = content_type
        newdoc = self.storagepool.store(newdoc, sourcefile)
        return newdoc
    
    
    def add(self, data, category='unknown', attributes={}, document_timestamp=None, content_type=None):
        """Store a bytestream."""
        
        if hasattr(data, 'read'):
            raise RuntimeError, "you provided a file object"
        mockfile = StringIO()
        mockfile.write(data)
        mockfile.seek(0)
        return self.add_file(mockfile, category, attributes, document_timestamp, content_type)
    
    
    def get(self, key):
        """Fetch a single Document from storage."""
        return self.session.query(Document).select(document_table.c.md5==self._cleankey(key))[0]
    
    
    def get_content(self, key):
        """Returns an iterable with the actual data of the document."""
        return self.session.query(Document).select(document_table.c.md5==self._cleankey(key))[0].file.read()
    
    
    def get_latest(self, limit=100, offset=0):
        """Get a list with the latest Documents."""
        return self.session.query(Document, lazy=False).select(limit=limit, offset=offset)
    
    
    def get_categories(self):
        """Returns a list of all category names."""
        ret = sqlalchemy.select([document_table.c.category],
                     group_by=[document_table.c.category]).execute().fetchall()
        return [x[0] for x in ret]
    
    
    def get_attributes(self):
        """Returns a list of all attribute names."""
        ret = sqlalchemy.select([docattribute_table.c.name],
                     group_by=[docattribute_table.c.name]).execute().fetchall()
        return [x[0] for x in ret]
    
    
    def search_by_attributes(self, limit=100, offset=0, **kwargs):
        """Return a list of Documente having a certain attribute with a certain value."""
        # TODO: make it work for more than one attribute:value pair
        restrictions = []
        for attrname, attrval in kwargs.items():
            restrictions.append(docattribute_table.c.name==attrname)
            restrictions.append(docattribute_table.c.value==attrval)
        return list(self.session.query(Document,
                                       lazy=False
                                       ).select(and_(*restrictions),
                                        limit=limit, offset=offset,
                                        from_obj=[document_table.join(docattribute_table)]))
    

storagepool_table = Table('storagepools', metadata,
    Column('id', Integer, primary_key=True),
    Column('path', String(), nullable=False),
    Column('url', String(), nullable=False),
    Column('active', Boolean, default=True, nullable=False),
    Column('filecount', Integer, default=0, nullable=False),
    Column('bytecount', Integer, default=0, nullable=False),
    )

document_table = Table('documents', metadata,
    Column('id', Integer, primary_key=True), # This is mainly for convinience during debugging
    Column('md5', String(32), nullable=False, default='', index=True, unique=True), # MD5 used lika an primary
    Column('sha1', String(40), nullable=False, default='', index=True, unique=True), # SHA-1
    Column('storagepool_id', Integer, ForeignKey('storagepools.id'), nullable=True),
    Column('path', String(), nullable=False, default=''),
    Column('category', String(), nullable=False, default=''),
    Column('content_type', String(), nullable=True),
    Column('document_timestamp', DateTime, PassiveDefault(func.current_timestamp()), nullable=True),
    Column('created_at', DateTime, PassiveDefault(func.current_timestamp()), nullable=False),
    )

docattribute_table = Table('documentattributes', metadata,
    Column('id', Integer, primary_key=True),
    Column('document_id', Integer, ForeignKey('documents.id'), nullable=True, index=True),
    Column('name', String(), nullable=False, index=True),
    Column('value', String(), nullable=False, index=True),
    UniqueConstraint('document_id', 'name'),
    )

Document_mapper = mapper(Document, document_table,
      properties = {'storagepool': relation(mapper(StoragePool, storagepool_table), backref='documents')},
      order_by=[desc(document_table.c.id)],
      )

Attribute_mapper = mapper(DocumentAttribute, docattribute_table,
      properties = {'document': relation(Document_mapper, backref='attributes')},
      order_by=[docattribute_table.c.name],
      )

