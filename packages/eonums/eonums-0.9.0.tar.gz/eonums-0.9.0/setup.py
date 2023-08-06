#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

from eonums import __version__, __date__, __license__, __author__


setupCommand = sys.argv[1]


# first try converting README from ReST to HTML, if Docutils is installed
# (else issue a warning)

if setupCommand in ("sdist", "build"):
    toolName = "rst2html.py"
    res = os.popen("which %s" % toolName).read().strip()
    if res.endswith(toolName):
        cmd = "%s '%s' '%s'" % (res, "README.txt", "README.html")
        print "running command %s" % cmd
        cmd = os.system(cmd)
    else:
        print "Warning: No '%s' found. 'README.{txt|html}'" % toolName,
        print "might be out of synch."


# description for Distutils to do its business

long_description = """\
`Eonums` is a simple module providing conversion between normal 
integer numbers and the corresponding textual expression in the 
`Esperano <http://en.wikipedia.org/wiki/Esperanto>`_ language. 
It was mainly developped in order to explore the regularity of 
Esperanto expressions for big integer numbers.

Names for 10**k (k = 6, 9, 12, ...) like "miliono" (10**6) or 
"miliardo" (10**9) are chosen from the so-called "Longa Skalo" 
as described on this page about 
`big numbers <http://eo.wikipedia.org/wiki/Numeralego>`_ 
(in Esperanto).

The integer numbers `eonums` can convert to or from such Esperanto 
expressions can be arbitrarily large, but are limited in practice
by the largest number for which there is a name in Esperanto (on
the "Longa Skalo")", which is, on the previous page, 10**63 
(dekiliardo). Hence, the largest integer you can handle with this 
module is 10**66 - 1. (This module makes no attempt to extend the 
Esperanto naming rules by introducing names like "undekiliono", 
"undekiliardo", "dudekiliono" etc.)

This module can be fully translated automatically to Python 3.0 
using its migration tool named ``2to3``. 


Features
++++++++

- convert Python integers to Esperanto integer strings (Unicode)
- convert Esperanto integer strings (Unicode) to Python integers
- validate Esperanto integer strings (Unicode)
- handle integers from 0 to 10**66 - 1
- provide conversion functions and command-line scripts
- provide a Unittest test suite
- can be automatically migrated to Python 3.0 using ``2to3``


Examples
++++++++

::

    >>> from eonums import int2eo, eo2int, validate_eo
    >>>
    >>> int2eo(22334455)
    u'dudek du milionoj tricent tridek kvar mil kvarcent kvindek kvin'
    >>>
    >>> eo2int(u"cent dudek tri")
    123
    >>> validate_eo(u"dudek cent tri")
    False
"""

classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Education",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Natural Language :: Esperanto",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Education",
    "Topic :: Software Development",
]

baseURL = "http://www.dinu-gherman.net/"

setup(
    name = "eonums",
    version = __version__,
    description = "A module for converting between integer numbers and Esperanto strings.",
    long_description = long_description,
    date = __date__,
    author = __author__,
    author_email = "gherman@darwin.in-berlin.de",
    maintainer = __author__,
    maintainer_email = "gherman@darwin.in-berlin.de",
    license = __license__,
    platforms = ["Posix", "Windows"],
    keywords = ["number", "conversion", "Esperanto"],
    url = baseURL,
    download_url = baseURL + "tmp/eonums-%s.tar.gz" % __version__,
    py_modules = ["eonums"],
    scripts = ["int2eo", "eo2int"],
    classifiers = classifiers,
)
