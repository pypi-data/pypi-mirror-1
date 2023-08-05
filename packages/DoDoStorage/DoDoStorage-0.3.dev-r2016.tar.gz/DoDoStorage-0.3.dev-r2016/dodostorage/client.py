#!/usr/bin/env python
# encoding: utf-8
"""
client.py

Created by Maximillian Dornseif on 2007-06-17.
Copyright (c) 2007 HUDORA GmbH. All rights reserved.
"""

from pkg_resources import require
require("huTools>=0.2.1.dev_r2005")

import os, md5
import httplib2, simplejson
import xml.etree.cElementTree as ET
from cStringIO import StringIO
from huTools.calendar.formats import rfc2616_date, rfc3339_date_parse

__revision__ = "$Revision: 2016 $"

class DoDoStorageError(Exception):
    """Generic Exception used by DoDoStorage generated Exceptions."""
    pass


class Document(object):
    """Represents a Document on the DoDoStorage Server."""
    
    def __init__(self, storageengine, data=None):
        self.attributes = []
        self.storageengine = storageengine
        self._data_cache = data
        self.key = None
        self.title = ''
    
    def _get_file(self):
        """Return the file associated with a document as an Python file Object."""
        mockfile = StringIO()
        mockfile.write(self._data)
        mockfile.seek(0)
        return mockfile
    file = property(_get_file)
    
    
    def _get_data(self):
        """Return an iterable representing the data stored in a document."""
        # files are iterables
        return [self._data]
    data = property(_get_data)
    
    
    def _get__data(self):
        """Returns the actual datastream - downloads and caces it when appropriate."""
        if not self._data_cache:
            response, body = self.storageengine.request('/document/%s/' % self.key)
            if response.status != 200:
                raise DoDoStorageError, body
            self._data_cache = body
            # TODO: check MD5, check Content-Length
            # TODO: use get_content() below
        return self._data_cache
    _data = property(_get__data)
    
    
    def update_attributes(self):
        """Convert DocumentAttribute objects into real attributes."""
        # This is called by our MapperExtension when the object is loaded from the DB
        for attr in self.attributes:
            setattr(self, attr.name, attr.value)
    
    
    def __len__(self):
        return len(self._data)
    
    
    def __str__(self):
        return self.title


class DocumentAttribute(object):
    """Represent attributes of a Document."""
    
    def __init__(self):
        self.name = ''
        self.value = None


class StorageEngine(object):
    """Coordinate and execute access to a DoDoStorage server instance."""
    def __init__(self, serverurl):
        super(StorageEngine, self).__init__()
        self.serverurl = serverurl
        self.http = httplib2.Http()
    
    def request(self, uripart, method='GET', body=None, headers={}):
        """Execute a HTTP request to our server."""
        if uripart.startswith('/'):
            uripart = uripart[1:]
        uri = os.path.join(self.serverurl, uripart) 
        return self.http.request(uri, method, body=body, headers=headers)
    
    
    def _parse_atom_entry(self, entry, document):
        """Expects an ATOM element-tree node and a document to enrich with the data from the elementtree."""
        document.title              = entry.find('{http://www.w3.org/2005/Atom}title').text
        document.category           = entry.find('{http://www.w3.org/2005/Atom}category').attrib.get('term')
        link                        = entry.find('{http://www.w3.org/2005/Atom}link')
        document.link               = link.attrib['href']
        document.contenttype        = link.attrib['type']
        document.document_timestamp = entry.find('{http://www.w3.org/2005/Atom}published').text
        document.document_timestamp = rfc3339_date_parse(document.document_timestamp)
        
        # extract further information from XHTML
        attname = attvalue = None
        for element in entry.find('{http://www.w3.org/2005/Atom}content').getiterator():
            # First the element key/id encoded in "name"
            if element.tag == '{http://www.w3.org/1999/xhtml}div' and element.attrib.get('name'):
                document.key = element.attrib.get('name')
            if (element.tag == '{http://www.w3.org/1999/xhtml}dl' and 
                'attributes' in element.attrib.get('class', '')):
                # we have reached the list of attributes
                for element in element.getiterator():
                    if element.tag == '{http://www.w3.org/1999/xhtml}dt':
                        attname = element.text
                    elif element.tag == '{http://www.w3.org/1999/xhtml}a':
                        attvalue = element.text
                    if attname and attvalue:
                        attr = DocumentAttribute()
                        attr.name = attname
                        attr.value = attvalue
                        document.attributes.append(attr)
                        setattr(document, attname, attvalue)
                        attname = attvalue = None
        return document
    
    
    def _parse_atom_feed(self, datastream):
        """Parse an Atom feed by parsing it's atom entries."""
        ret = []
        for entry in ET.fromstring(datastream).findall('{http://www.w3.org/2005/Atom}entry'):
            ret.append(self._parse_atom_entry(entry, Document(self)))
        return ret
    
    
    def add_file(self, sourcefile, category='unknown', attributes={}, document_timestamp=None,
                 contenttype='application/octet-stream'):
        """Add a file identified by a filenale or a file()-Object to the DoDoStorage Server."""
        if not hasattr(sourcefile, 'read'):
            # we assume, this is not a file object fut a pathname, so open it
            sourcefile = open(sourcefile, 'rb')
        data = sourcefile.read()
        return self.add(data, category, attributes, document_timestamp, contenttype)
    
    
    def add(self, data, category='unknown', attributes={}, document_timestamp=None,
            contenttype='application/octet-stream'):
        """Add a stream of bytes to the DoDoStorage Server."""
        newdoc = Document(self, data)
        headers = {'X-de.hudora.dodostor-Attributes': simplejson.dumps(attributes, sort_keys=True),
                   'X-de.hudora.dodostor-Category': category,
                   'Content-Type': contenttype,
                   'Content-MD5': md5.new(data).hexdigest()}
        if document_timestamp:
            headers['X-de.hudora.dodostor-Timestamp'] = rfc2616_date(document_timestamp)
        
        response, body = self.request('/documents/', 'POST', data, headers=headers)
        if response['status'] != '201':
            raise DoDoStorageError, repr((data, headers, body, response))
        entry  =  ET.fromstring(body).find('{http://www.w3.org/2005/Atom}entry')
        self._parse_atom_entry(entry, newdoc)
        return newdoc
    
    
    def get(self, key):
        """Retrives a document from the DoDoStorage server and returns a Document Object."""
        newdoc = Document(self)
        response, body = self.request('/document/%s/metadata.atom' % key)
        if response.status != 200:
            raise DoDoStorageError, body
        entry  =  ET.fromstring(body).find('{http://www.w3.org/2005/Atom}entry')
        self._parse_atom_entry(entry, newdoc)
        return newdoc
    
    
    def get_content(self, key):
        """Returns an iterable with the actual data of the document."""
        response, body = self.request('/document/%s/' % key)
        if response.status != 200:
            raise DoDoStorageError, body
        # TODO: check MD5, check Content-Length
        return body
    
    
    def get_latest(self, limit=100):
        """Get a list of the most recently added Documents from the DoDoStorage Server."""
        # TODO: add support for start and limit on server site.
        response, body = self.request('/documents/')
        if response.status != 200:
            raise DoDoStorageError, body
        return self._parse_atom_feed(body)[:limit]
    
    
    def search_by_attributes(self, **kwargs):
        """Get a list of Documents matchin an attribute==value condition from the Server."""
        # TODO: add support for start and limit on server site.
        # TODO: clean strings hashval = re.sub('^[a-zA-Z0-9-._]', ' ', hashval).replace('..', '~~')
        for key, value in kwargs.items():
            response, body = self.request('/documents/search/%s/%s/' % (key, value))
            if response.status != 200:
                raise DoDoStorageError, body
        return self._parse_atom_feed(body)
    
    
    def get_categories(self):
        """Returns a list of all category names."""
        raise NotImplementedError
    
    def get_attributes(self):
        """Returns a list of all attribute names."""
        raise NotImplementedError
