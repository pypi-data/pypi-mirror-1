#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
from distutils.core import setup

sys.path.insert(0, "src")

from fileinfo import __version__, __date__, __license__, __author__


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

baseURL = "http://www.dinu-gherman.net/"

setup(
    name = "fileinfo",
    version = __version__,
    description = "Show information about files in a tabular fashion.",
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
a global huge index and it presents not only a flat result list, but an 
overview of matching files together with the respective (possibly sorted) 
attribute values. And since `fileinfo` is purely written in Python it is 
not tied to a specific plattform.

`Fileinfo` is most useful when used on many files at once, because then 
you get an overview of the attribute values for the entire set of files.""",
    date = __date__,
    author = __author__,
    author_email = "gherman@darwin.in-berlin.de",
    maintainer = __author__,
    maintainer_email = "gherman@darwin.in-berlin.de",
    license = __license__,
    platforms = ["Posix", "Windows"],
    keywords = ["files", "access information", "tabular display"],
    url = baseURL,
    download_url = baseURL + "tmp/fileinfo-%s.tar.gz" % __version__,
    package_dir = {"fileinfo": "src/fileinfo"},
    packages = [
        "fileinfo", 
        "fileinfo.plugins", 
        "fileinfo.test", 
        "fileinfo.guidjango", 
        "fileinfo.test.examples",
    ],
    package_data = {
        "fileinfo": ["test/examples/*", "guidjango/templates/*"],
    },
    scripts = ["scripts/fileinfo"],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ]
)


# simulate setup option "package_data" for Python < 2.4

if sys.version_info[:2] < (2, 4) and setupCommand in ("build", "install"):
    # Distutils copies the addidional data files itself during "install"
    import sys, glob, shutil
    from os.path import join
    for (k, v) in package_data.items():
        for f in v:
            files = glob.glob(join(k, f))
            for src in files:
                dst = join("build/lib", src)
                print "copying %s -> %s" % (src, dst)
                shutil.copy2(src, dst)
