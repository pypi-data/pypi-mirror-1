#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"Project meta information"


__version__ = "0.3.3"
__license__ = "GNU General Public Licence v3 (GPLv3)"
__author__ = "Dinu Gherman"
__date__ = "2008-11-14"


name = "fileinfo"
version = __version__
date = __date__
description = "Show information about files in a tabular fashion."
long_description = """\
`Fileinfo` helps you in identifying files with specific values for certain 
attributes in order to search and sort these files and present the results 
in an easily readable tabular fashion.

Using `fileinfo` you can access this information for many files at once 
without opening these files individually with a dedicated application, 
which can be very time consuming.

In order to determine such file attributes, `fileinfo` comes with some 
pre-built plug-ins, for file formats like PDF, MP3, TTF and PY (Python 
source code files). These plug-ins allow you to determine e.g. the number 
of pages or the creator of PDF documents, the artist and title of MP3 
files, the number of glyphs in TTF font files, the number of classes 
or docstrings in Python files, etc. 

Of course, you can also access file information on an operating system 
level, like the size and modification date/time of files. And, you can 
also write your own plug-ins to extend `fileinfo`'s capabilities.

A tool like `fileinfo` is different from other tools like `Spotlight 
<http://www.apple.com/macosx/features/spotlight/>`_, since it does not use 
a huge global index and it presents not only a flat result list, but an 
overview of matching files together with the respective (possibly sorted) 
attribute values. And since `fileinfo` is written in pure Python it is 
not tied to a specific plattform.

`Fileinfo` is most useful when used on many files at once, because then 
you get an overview of the attribute values for the entire set of files.

This release fixes a few buglets and implements minor packaging refactorings.


Features
++++++++

- extract file attributes 
- display attribute values in a tabular fashion
- display output table as plain text, CSV, simple RestructuredText, HTML
- display output table interactively (OS X Cocoa and Django, experimental)
- sort output by one or more attribute values
- filter files with attributes satisfying some expression
- provide a plugin architecture
- provide a plugin for filesystem attributes
- provide plugins for XML and Python
- provide plugins for Spotlight attributes and file bundles (OS X)
- provide plugins for media formats PDF, MP3 and Quicktime (experimental)
- install a Python package named ``fileinfo``
- install a Python command-line script named ``fileinfo``
- provide a Unittest test suite
- install test suite inside the installed package 
- test samples include MP3, PDF, TTF and Python files


Examples
++++++++

From the system command-line you use `fileinfo` e.g. like this::

  $ python fileinfo -a npages *.pdf
  
Here is an example of some statistics for Python code (taken from the 
top-level of `Docutils <http://docutils.sourceforge.net/>`_ 0.5)::

  $ cd docutils-0.5/build/lib/docutils
  $ fileinfo -a lc:nclasses:ndefs:ndocstrs *.py
    lc  nclasses  ndefs  ndocstrs  path
   205         5      2         3  __init__.py
   616         1     24        14  core.py
    97         0      3         4  examples.py
   760         5     34        18  frontend.py
   413         9     22        14  io.py
  1802       130    124        39  nodes.py
  1491        19     91        60  statemachine.py
   137         0      0         1  urischemes.py
   594         9     32        25  utils.py
  6115       178    332       178  total

Here is another example for Mac OS X Widgets::

  $ cd /Library/Widgets
  $ fileinfo --format rest-simple -a bundlename:bundleversion *.wdgt
  =================  =============  ======================
  bundlename         bundleversion  path
  =================  =============  ======================
  Address Book       1.1.5          Address Book.wdgt
  Calculator         1.2            Calculator.wdgt
  Dictionary         2.0.1          Dictionary.wdgt
  Flight Tracker     1.3            Flight Tracker.wdgt
  Movies             0.4            Movies.wdgt
  Stickies           2.0            Stickies.wdgt
  Stocks             1.3            Stocks.wdgt
  Tile Game          1.0.2          Tile Game.wdgt
  Unit Converter     2.2            Unit Converter.wdgt
  Weather            1.1            Weather.wdgt
  WebClip            1.0            Web Clip.wdgt
  World Clock        2.0            World Clock.wdgt
  Calendar           3.1            iCal.wdgt
                                    total
  =================  =============  ======================
"""
author = __author__
author_email = '@'.join(['gherman', 'darwin.in-berlin.de'])
maintainer = author
maintainer_email = author_email
license_short = 'GNU GPL'
license = __license__
platforms = ["Posix", "Windows"]
keywords = ["files", "attributes", "information", "tabular display"]
_baseURL = "http://www.dinu-gherman.net/"
url = _baseURL
download_url = _baseURL + "tmp/%s-%s.tar.gz" % (name, __version__)
package_dir = {"fileinfo": "src/fileinfo"}
packages = [
    "fileinfo", 
    "fileinfo.plugins", 
    "fileinfo.test", 
    "fileinfo.guidjango", 
    "fileinfo.test.examples",
]
package_data = {
    "fileinfo": ["test/examples/*", "guidjango/templates/*"],
}
py_modules = []
scripts = ["scripts/fileinfo"]
classifiers = [
    # see http://pypi.python.org/pypi?%3Aaction=list_classifiers
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Topic :: Utilities",
]
