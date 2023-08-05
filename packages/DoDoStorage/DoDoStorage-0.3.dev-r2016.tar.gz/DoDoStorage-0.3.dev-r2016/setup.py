#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Maximillian Dornseif on 2007-06-23.
Copyright (c) 2007 HUDORA GmbH. BSD Licensed.
"""

from setuptools import setup, find_packages

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
            
setup(name='DoDoStorage',
      version='0.3',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      url='http://www.hudora.de/code/',
      description='User-Space write-once Network Filesystem',
      long_description='''DoDoStorage is meant as a User-Space write-once Filesystem. Much Inspiration
      is drawn from MoglieFS http://www.danga.com/mogilefs/ - but DoDoStorage it is
      much simpler.
      
      With DoDoStorage you can store files - "Documents" in DoDoStorage speak. For
      each file you get an opaque "Document key" to retrive it. Stored Files are
      immutable - you can't change or delete them. Every Document has an
      "category" whichs help to destinguish classes of Documents, a mime-type and
      a timestamp. It also has a set of arbitrary attributes.
      
      DoDoStorage is meant to be accessed via an RESTful HTTP API.''',
      license='BSD',
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python'],
      
      scripts = ['dodostorage/dodoserver'],
      install_requires = ['huTools', 'httplib2', 'simplejson', 'selector', 'sqlalchemy>=0.3'],
      packages = find_packages(),
      test_suite = "dodostorage.test"

)
