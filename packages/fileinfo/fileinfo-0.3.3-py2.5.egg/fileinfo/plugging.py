#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""Simple plug-in mechanim.


"""


import sys, glob, os, os.path
from os.path import dirname, basename, abspath, pathsep, join, splitext


def getPluginsFromModule(mod, baseClass):
    "Return all plug-in classes contained in a loaded module."

    res = [
        obj for (name, obj) in mod.__dict__.items() 
        if type(obj) == type
            and obj != baseClass
            and issubclass(obj, baseClass)
    ]
    return res


def loadPlugins(baseClass, filenamePattern, folder=None, envVar=None):
    "Search, load oad and return list of plugin classes from known places."

    paths = []

    # add given folder to the list of search places
    if folder != None:
        paths = [folder]

    # add places indicated by environment variable, if present
    if envVar and envVar in os.environ:
        paths += os.environ[envVar].split(os.path.pathsep)

    # import specific Python plug-in modules
    # and return a list of all plug-in classes found inside 
    plugins = []
    for path in paths:
        modPaths = glob.glob(join(path, filenamePattern))
        for mp in modPaths:
            dn = dirname(mp)
            mn = basename(splitext(mp)[0])
            sys.path.insert(0, dn)
            mod = __import__(mn)
            # print "***", [v for (k, v) in mod.__dict__.items()]
            invs = getPluginsFromModule(mod, baseClass)
            del sys.path[0]
            plugins += invs
    
    return plugins

