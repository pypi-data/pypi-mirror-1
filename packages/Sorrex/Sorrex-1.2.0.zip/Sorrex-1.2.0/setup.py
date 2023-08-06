#!-*- coding:utf-8 -*-

from setuptools import setup, find_packages

PACKAGE_NAME    = "Sorrex"
PACKAGE_VERSION = "1.2.0"
SUMMARY     = "Sorrex parser in Python."
DESCRIPTION = "This module provides parser function of Sorrex."

setup(
    name    = PACKAGE_NAME,
    version = PACKAGE_VERSION,
    description      = SUMMARY,
    long_description = DESCRIPTION,
    
    packages = find_packages(),
    exclude_package_data = { '': ['*.pyy', '*.code'] },
    
    url          = 'http://code.google.com/p/sorrex/',
    author       = 'ruby-U',
    author_email = 'ruby.u.g@gmail.com',
    
    license   = 'MIT',
    platforms = ['Any'],
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Natural Language :: Japanese',
                   'Topic :: Text Processing',
                   ],
)
