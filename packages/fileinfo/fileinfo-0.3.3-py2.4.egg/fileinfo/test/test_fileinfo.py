#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Unittests for fileinfo package.

This file will not work when running it from inside its directory
with "python test_fileinfo.py". Run it instead from within fileinfo 
itself using the following command in a terminal:

  fileinfo -t
"""


import os, sys, unittest, glob
from os.path import dirname, basename, abspath, pathsep, join, splitext, isdir

from fileinfo import fileinfo
from fileinfo import investigator


class FileinfoTestCase(unittest.TestCase):

    def test0(self):
        "Test finding filenames in a directory without any attributes."

        examples = join(dirname(__file__), "examples", "*.py")
        paths = glob.glob(examples)
        exp = [[basename(p)] for p in paths]
        res = fileinfo.process(examples)
        self.assertEqual(res, exp) 


    def test1(self):
        "Test finding attributes of a Python script file."

        from examples.pythoncode import results as exp

        path = join(dirname(__file__), "examples", "pythoncode.py")
        sep = fileinfo.ATTR_SEP
        attrs = sep.join("lc nclasses ndefs ncomments nstrs nkws ndkws".split())
        res = fileinfo.process(path, a=attrs)
        
        z = zip(attrs.split(fileinfo.ATTR_SEP), res[0][:-1])
        res = dict(z)

        self.assertEqual(res, exp) 


    def test2(self):
        "Test finding attributes of a PDF file."

        path = join(dirname(__file__), "examples", "digits.pdf")
        exp = [10, "AUTHOR", "PRODUCER", basename(path)]

        sep = fileinfo.ATTR_SEP
        attrNames = "npages author producer".split()
        res = fileinfo.process(path, a=sep.join(attrNames))
        res = res[0]
        
        self.assertEqual(res, exp) 


    def test3(self):
        "Test finding attributes of a TTF file."

        path = join(dirname(__file__), "examples", "Rina.ttf")
        exp = [270, basename(path)]

        res = fileinfo.process(path, a="maxp.numGlyphs")
        res = res[0]
        
        self.assertEqual(res, exp) 


    def test4(self):
        "Test finding attributes of an MP3 file."

        path = join(dirname(__file__), "examples", "bell.mp3")
        exp = ["The Bell", "Best of The Bell", basename(path)]

        sep = fileinfo.ATTR_SEP
        res = fileinfo.process(path, a=sep.join("artist album".split()))
        res = res[0]
        
        self.assertEqual(res, exp) 


    def test5(self):
        "Test finding/adding custom plug-in investigator via env. variable."

        # add directory containing this module file to os.environ variable
        OSEPVN = fileinfo.OS_ENVIRON_PLUGIN_VARNAME
        paths = os.environ.get(OSEPVN, "").split(fileinfo.ATTR_SEP)
        paths.append(dirname(__file__))
        os.environ[OSEPVN] = fileinfo.ATTR_SEP.join(paths)

        # load plug-ins and add them to known plug-ins
        plugins = fileinfo.plugging.loadPlugins(
            investigator.BaseInvestigator, 
            "fileinfo_inv_plugin_*.py", 
            envVar=OSEPVN)
        fileinfo.INVESTIGATOR_CLASSES += plugins

        # remove directory containing this module file from os.environ variable
        os.environ[OSEPVN] = fileinfo.ATTR_SEP.join(paths[:-1])

        invc = fileinfo.INVESTIGATOR_CLASSES[-1]
        self.assert_(invc.__name__ == "TestInvestigator") 


    def test6(self):
        "Test adding and using a custom plug-in investigator."

        from fileinfo_inv_plugin_test import TestInvestigator
        fileinfo.INVESTIGATOR_CLASSES.append(TestInvestigator)
        
        path = __file__
        if __file__.endswith(".pyc"):
            path = path[:-1]
            
        res = fileinfo.process(path, a="foo")
        res = res[0][0]
        exp = "bar"
        self.assertEqual(res, exp) 


    def test7(self):
        "Test determining the number of docstrings in a Python file."

        path = join(dirname(__file__), "examples", "docstrings.py")
        res = fileinfo.process(path, a="ndocstrs")
        res = res[0][0]
        exp = 7
        self.assertEqual(res, exp) 


    def test8(self):
        "Test determining the number of import statements in a Python file."

        path = join(dirname(__file__), "examples", "imports.py")
        exp = [12, 8, basename(path)]

        sep = fileinfo.ATTR_SEP
        res = fileinfo.process(path, a=sep.join("nimpstmts nimpsrcs".split()))
        res = res[0]
        
        self.assertEqual(res, exp) 


    def test9(self):
        "Test determining the number and list of decorators in a Python file."

        path = join(dirname(__file__), "examples", "decorators.py")
        exp = [4, ['bar', "c.meth", "foo"], basename(path)]

        sep = fileinfo.ATTR_SEP
        res = fileinfo.process(path, a=sep.join("ndecs decs".split()))
        res = res[0]
        
        self.assertEqual(res, exp) 


if __name__ == "__main__":
    print "This module should be tested (after installing fileinfo)"
    print "from the command-line like this:"
    print "  fileinfo -t"
