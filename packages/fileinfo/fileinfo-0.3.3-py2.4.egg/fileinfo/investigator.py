#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""Abstract base class for file investigators.

An investigator has a dict. attribute 'attrMap', which maps
attr. names or regular expresions to method names.
"""

import sys, time, datetime, os.path, stat, re
from os.path import isdir, isfile, islink, getsize, isabs, getmtime


if sys.platform == "darwin":
    try:
        from Carbon.File import FSResolveAliasFile, FSRef
        HAVE_CARBON = True
    except ImportError:
        HAVE_CARBON = False


if sys.platform == "darwin" and HAVE_CARBON:
    #def resolveAlias(path):
    #    "Resolve a Carbon alias file, or return unchanged."
    #    
    #    return FSResolveAliasFile(path, True)[0].as_pathname()
    
    def isAlias(path):
        "Is this a Carbon alias file?"
        
        return bool(FSRef(path).FSIsAliasFile()[0])
        
    os.path.isalias = isAlias


# stuff for calculating statistical values over multiple records

def getSum(attrName, recs):
    "Return sum of a given attribute name for a list of records."
    
    total = 0
    for r in recs:
        s = getattr(r, attrName)
        if s != "n/a":
            total += s
    
    return total


class BaseInvestigator(object):
    "An abstract class for determining attributes of files."

    attrMap = {
        # "attrName": "methName", 
        # "attrNameExpr": "methName", 
    }
    
    totals = ()
    
    def __init__(self, path):
        self.path = path        
    
        
    def activate(self):
        "Try activating self, setting 'active' variable."
        
        self.active = False            
        return self.active
        
        
    def getFunc(self, attrName):
        "Return access method for attribute named 'attrName'."
        
        funcName = self.attrMap[attrName]
        return getattr(self, funcName)


    # stuff to calculate attributes with a given name for this investigator
    
    def getAttrValue(self, attrName):
        "Return value for attribute named 'attrName'."

        # if attrName in attrMap.keys() call the respective method 
        if attrName in self.attrMap.keys():
            funcName = self.attrMap[attrName]
            if funcName == None:
                return None
            return getattr(self, funcName)()
        
        # else use first match with attrMap.keys() as reg. exprs.
        else:
            matchingAttrNames = [an 
                for an in self.attrMap.keys() if re.match(an, attrName)]
            if matchingAttrNames:
                funcName = self.attrMap[matchingAttrNames[0]]
                return getattr(self, funcName)(attrName)
        
        return None
