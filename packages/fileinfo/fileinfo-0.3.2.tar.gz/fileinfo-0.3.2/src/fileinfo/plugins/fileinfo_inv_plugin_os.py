#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for basic OS-related file operations.
"""


import sys, time, datetime, os.path, stat
from os.path import isdir, isfile, islink, getsize, isabs, getmtime

from fileinfo.investigator import BaseInvestigator


if sys.platform == "darwin":
    try:
        from Carbon.File import FSResolveAliasFile, FSRef
        HAVE_CARBON = True
    except ImportError:
        HAVE_CARBON = False


if sys.platform == "darwin" and HAVE_CARBON:    
    def isAlias(path):
        "Is this a Carbon alias file?"
        
        return bool(FSRef(path).FSIsAliasFile()[0])
        
    os.path.isalias = isAlias


class OSInvestigator(BaseInvestigator):
    "A class for determining attributes of files." #:fix:#

    attrMap = {
        "size": "getSize",
        "mtime": "getmtime",
        "uid": "getuid",
        "username": "getUsername",
        "type": "getType",
        "level": "getNestingLevel",
    }
    
    totals = ("size")
    
    def activate(self):
        "Try activating self, setting 'active' variable."
        
        self.active = True            
        return self.active
        
        
    def getType(self):
        "Return the type of a file."
        
        typ = "?"
        if isfile(self.path):
            typ = "r"
        elif isdir(self.path):
            typ = "d"
        elif islink(self.path):
            typ = "l"

        if sys.platform == "darwin" and HAVE_CARBON:
            if os.path.isalias(self.path):
                typ = "a"
            
        return typ
        
    
    def getSize(self):
        "Return the size of a file."
        
        return getsize(self.path)
        
    
    def getmtime(self):
        "Return the last modification time of a file."
        
        t = getmtime(self.path)
        utc = datetime.datetime.utcfromtimestamp(t).isoformat()
        if "." in utc:
            utc = utc[:utc.find(".")]
            
        return utc
    
    
    def getuid(self):
        "Return the numeric user ID of a file."
        
        return os.stat(self.path)[stat.ST_UID]
        

    def getUsername(self):
        "Return the user login name of the owner of a file."
        
        import pwd
        st = os.stat(self.path)[stat.ST_UID]
        username = pwd.getpwuid(st)[0]
        
        return username
        

    def getNestingLevel(self):
        "Return absoulte nesting level."
    
        # root directory has level 0
        level = abspath(self.path).count(os.path.sep) - 1
        
        return level
