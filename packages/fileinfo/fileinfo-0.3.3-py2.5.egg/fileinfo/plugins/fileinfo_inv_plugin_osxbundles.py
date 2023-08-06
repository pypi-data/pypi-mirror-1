#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for Mac OS X bundles.

This makes sense only on Mac OS X.
"""


import os, sys, shutil, tempfile
from os.path import join, exists, basename, splitext, dirname

from fileinfo.investigator import BaseInvestigator


def readPlistFile(path):
    "Read content of property list file, either XML or binary."

    try:
        from Foundation import NSDictionary
        plist = NSDictionary.dictionaryWithContentsOfFile_(path)
    except:
        try:
            # try XML format
            # (not sure if 'plistlib' is available on Windows, Linux?)
            from plistlib import readPlist 
            plist = readPlist(path)
        except:
            # try binary format        
            fd, destPath = tempfile.mkstemp()
            shutil.copy2(path, destPath)
            os.popen("plutil -convert xml1 '%s'" % destPath)
            plist = readPlist(destPath)
            os.remove(destPath)
        
    return plist


class OSXBundleInvestigator(BaseInvestigator):
    "A class for determining attributes of OS X bundles."

    attrMap = {
        "bundlename": "getName",
        "bundleversion": "getVersion",
        "bundleminsysversion": "getMinSysVersion",
    }

    totals = ()
        
    def activate(self):
        "Try activating self, setting 'active' variable."
        
        path = self.path        
        base = splitext(basename(path))[0]
        if exists(join(path, "Contents", "Info.plist")):
            plPath = join(path, "Contents", "Info.plist")
            self.active = True
            self.plist = readPlistFile(plPath)
        elif exists(join(path, "Info.plist")):
            plPath = join(path, "Info.plist")
            self.plist = readPlistFile(plPath)
            self.active = True
        else:
            self.active = False

        return self.active


    def getName(self):
        "Return OS X bundle name."

        if not self.active:
            return "n/a"

        try:
            nameString = self.plist["CFBundleName"]
        except:
            nameString = "n/a"

        return nameString


    def getVersion(self):
        "Return OS X bundle version."

        if not self.active:
            return "n/a"

        try:
            versionString = self.plist["CFBundleShortVersionString"]
        except:
            try:
                versionString = self.plist["CFBundleVersion"]
            except:
                versionString = "n/a"

        return versionString


    def getMinSysVersion(self):
        "Return OS X bundle minimum system version."

        if not self.active:
            return "n/a"

        try:
            versionString = self.plist["LSMinimumSystemVersion"]
        except:
            versionString = "n/a"

        return versionString
