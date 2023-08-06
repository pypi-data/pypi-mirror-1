#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for accessing Subversion information.

Sample output for "svn info log.py"

Path: log.py
Name: log.py
URL: svn+foo://svn.foo.com/projects/bar/common/lib/log.py
Repository Root: svn+foo://svn.foo.com/bar
Repository UUID: 8989e680-f916-11dd-b985-fbdf42762348
Revision: 1114
Node Kind: file
Schedule: normal
Last Changed Author: mal
Last Changed Rev: 1087
Last Changed Date: 2009-04-29 20:39:39 +0200 (Mi, 29 Apr 2009)
Text Last Updated: 2009-04-30 10:11:20 +0200 (Do, 30 Apr 2009)
Checksum: 917edbe0863a1677da97aa48193c623d
"""

import os
import re
import types
from os.path import dirname, join, exists

from fileinfo.investigator import BaseInvestigator


def getInfoAttr(pathOrInfolines, attrName):
    "Return attribute of 'svn info' command for a file."

    poi = pathOrInfolines
    if type(poi) == types.StringTypes and exists(poi):
        cmd = "svn info '%s'"
        sin, sout, serr = os.popen3(cmd % poi)
        infolines = sout.readlines()
    else:
        infolines = pathOrInfolines
        
    lines = [line for line in infolines if line.startswith(attrName)]

    if len(lines) == 1:
        line = lines[0]
        res = line[len(attrName) + 1:].strip()
        return res
    else:
        return ""


class SubversionInvestigator(BaseInvestigator):
    "A class for attributes of files under Subversion version control."

    attrMap = {
        "rev": "getRevision",
        "lastchrev": "getLastChangedRevision",
        "lastchauth": "getLastChangedAuthor",
        "state": "getState",
        "numci": "getNumCheckins",
    }

    totals = ["numci"]

    def __init__(self, path):
        self.path = path
        self.infolines = []

                
    def activate(self):
        "Try activating self, setting 'active' variable."

        svnDir = join(dirname(self.path), ".svn")
        if not exists(svnDir):
            self.active = False
        else:
            cmd = "svn info '%s'"
            sin, sout, serr = os.popen3(cmd % self.path)
            self.infolines = sout.readlines()
            self.active = True

        return self.active
        
        
    def getRevision(self):
        "Return the revision number of a file."
    
        res = getInfoAttr(self.infolines, "Revision:")
        try:
            return int(res)
        except ValueError:
            return res


    def getLastChangedRevision(self):
        "Return the last changed revision number of a file."
    
        res = getInfoAttr(self.infolines, "Last Changed Rev:")
        try:
            return int(res)
        except ValueError:
            return res
                
    
    def getLastChangedAuthor(self):
        "Return the last changed author of a file."
    
        return getInfoAttr(self.infolines, "Last Changed Author:")
                
    
    def getState(self):
        "Return the Subversion state of a file."
        
        cmd = "svn stat '%s'"
        info = os.popen3(cmd % self.path)[1].read()
        if len(info) == 0:
            return ""
        else:
            return info[0]


    def getNumCheckins(self):
        "Return the number of checkins of a file."
        
        cmd = "svn log '%s'"
        log = os.popen3(cmd % self.path)[1].readlines()
        revLines = [l for l in log if re.match("r\d+.*", l)]

        return len(revLines)
