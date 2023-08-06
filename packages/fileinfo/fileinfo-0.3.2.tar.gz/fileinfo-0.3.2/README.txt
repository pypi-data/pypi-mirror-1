.. -*- mode: rst -*-

========
Fileinfo
========

---------------------------------------------------------------
Investigate and present file attributes in a tabular fashion.
---------------------------------------------------------------

:Author:     Dinu Gherman <gherman@darwin.in-berlin.de>
:Homepage:   http://www.dinu-gherman.net/
:Version:    Version 0.3.2
:Date:       2008-07-07
:Copyright:  GNU Public Licence v3 (GPLv3)


About
-----

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
you get an overview of the attribute values for the entire set of files.


Examples
--------

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


Installation
------------

After downloading the file ``fileinfo-0.3.2.tar.gz`` in your download
directory, change into this directory and run the following command 
to unpack `fileinfo`::

  $ tar xfz fileinfo-0.3.2.tar.gz

Then change into the newly created directory ``fileinfo`` and install 
`fileinfo` by running the following command::

  $ python setup.py install

This will install a Python package named `fileinfo` in the 
``site-packages`` subfolder of your Python interpreter and a script 
tool named ``fileinfo`` in your ``bin`` directory, usually in 
``/usr/local/bin``.


Dependencies
------------

Some of `fileinfo`'s plug-ins use additional Python packages that 
you might have to install if you want to use the functionality 
provided by these plugins. The current version of `fileinfo` does
not yet provide a consistent and clean mechanism for reporting such 
missing packages by third parties. But this is on the todo list.

Django, WxPython, ObjC, psi


Testing
-------

`Fileinfo` comes with a built-in Unittest test suite which can be run 
after installation with the command-line options ``-t`` or ``--test`` 
like this::
 
  $  fileinfo --test
  ........
  ---------------------------------------------------------
  Ran 9 tests in 0.550s

  OK


Bug reports
-----------

Please report bugs and patches to Dinu Gherman 
<gherman@darwin.in-berlin.de>. Don't forget to include information 
about the operating system and Python versions being used.
