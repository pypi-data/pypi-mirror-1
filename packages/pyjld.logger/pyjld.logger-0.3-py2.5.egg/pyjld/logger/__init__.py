#!/usr/bin/env python
"""
pyjld.logger: cross-platform logging utilities

This package consists mainly of:

    * MsgLogger: cross-platform logger with message translation
    * logger: a *ready-to-go* logger
    * xcLogger: a cross-platform syslog logger

=========
Changelog
=========

**0.3** 

* More robust ``messages`` look-up in MsgLogger

**0.2**

* Added ``MsgLogger``

@author: Jean-Lou Dupont
"""
__author__  = "Jean-Lou Dupont"
__email     = "python (at) jldupont.com"
__version__ = "0.3"
__fileid    = "$Id: __init__.py 22 2009-04-02 01:21:13Z jeanlou.dupont $"

__dependencies = []

__classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: Public Domain',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    ]

from logger import *