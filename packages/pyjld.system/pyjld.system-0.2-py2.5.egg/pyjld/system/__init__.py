#!/usr/bin/env python
""" 
pyjld.system: various system level utilities (e.g. daemon, cross-platform registry, command-line tools)

This package contains various system level utilities.

=========
Changelog
=========

*0.2*  

* Added command-line related utilities
* Added a cross-platform ``registry`` utility


@author: Jean-Lou Dupont
"""
__author__  = "Jean-Lou Dupont"
__email     = "python (at) jldupont.com"
__version__ = "0.2"
__fileid    = "$Id: __init__.py 37 2009-04-03 01:58:16Z jeanlou.dupont $"


__classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: Public Domain',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    ]

__dependencies = ['python_daemon',]

