#!/usr/bin/env python
# -*- coding: utf-8 -
#
from setuptools import setup


import os
import sys

setup(
    name = 'py-simplecouchdb',
    version = '0.9.24',

    description = 'Simple CouchDB library',
    long_description = \
"""CouchDB is document oriented database. Simple Couchdb Library try
to keep its simplicity when you manage it in python""",
    author = 'Benoit Chesneau',
    author_email = 'benoitc@e-engura.com',
    license = 'Apache License 2',
    url = 'http://code.google.com/p/py-simplecouchdb/',
    zip_safe = False,

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = ['simplecouchdb', 'simplecouchdb.client', 'simplecouchdb.schema', 'simplecouchdb.schema.properties'],
        
    zip_safe = False,

    setup_requires = [
        'setuptools>=0.6b1',
        'httplib2',
        'simplejson'
    ]


)
