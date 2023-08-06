#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for accessing the Spotlight database on Mac OS X.

This calls a tool named 'mdls' which exists only on Mac OS X. This is 
very experimental and the function parsing the output of 'mdls' needs 
to be further debugged and completed.
"""


import sys, os.path, re, commands 
from pprint import pprint as pp

from fileinfo.investigator import BaseInvestigator


def parseKmdOutput_single_attr(path, attrName):       
    "Run Spotlight 'mdls' command on a file and return result for single attr."    

    # run 'mdls' command, grab its output and remove newlines
    output = commands.getoutput(str("mdls -name %s %s" % (attrName, path)))
    m = re.match("(\w+) *= *(.*)", output)
    if m:
        name, val = m.groups()
        # print "***", name, val
        try:
            val = eval(val)
        except (SyntaxError, NameError):
            pass
    else:
        val = None
        
    print "***", path, attrName, val
            
    return val
        

# deprecated and no longer used
def _parseKmdOutput(path):       
    "Run Spotlight 'mdls' command on a file and return result as a Python dict."    
    # needs special handling of date fields like "2007-05-24 13:08:05 +0200"

    # run 'mdls' command, grab its output and remove newlines
    output = commands.getoutput(str("mdls " + path))
    print "***", output
    s = output.replace('\n', '')
    
    # handle attributes as added by "Python Metadata Importer", 1.0.6,
    # see http://toxicsoftware.com/python_metadata_importer_106_released
    for name in ('org_python_functions', 'org_python_classes'):
        s = s.replace(name, 'kMDItem' + name)
    
    # split the string on 'kMD' into lines
    kmdLines = s.split('kMD')
    kmdLines = [line for line in kmdLines if line]
    # print "** kmdLines"
    # pp(kmdLines)
    items = [re.match("(\w+) *= *(.*)", line) for line in kmdLines]
    items = [m.groups() for m in items if m]
    # print "** items"
    # pp(items)
    
    # reinsert kMD
    items = [("kMD" + k, v) for (k, v) in items]
    # print "** items"
    # pp(items)

    # work around a feature in Mac OS X 
    # (which puts no quotes around 'simple' strings)
    pairs = []
    for item in items:
        try:
            k, v = item
        except:
            # print "### item", item
            # print path
            raise
        v = v.strip()
        try:
            ev = eval(v)
        except:
            # print "### failed evaluating", repr(v)
            if v[0] not in ('"', "'"):
                v = v.replace('"', '')
                v = v.replace("'", '')
            if v.startswith('('): # and v.startswith(')'):
                # print "---", v
                v = re.sub("(\w+)", lambda m:'"%s"' % m.groups()[0], v)
            # also turn a single name into a one element tuple
            # print "****", repr(v)
            # if type(eval(v)) == str:
            #     v = "(%s,)" % v
        # print "***", repr(v)
        try:
            pairs.append([k, eval(v)])
        except SyntaxError:
            pairs.append([k, v])
    
    data = dict(pairs)
    
    return data


class SpotlightInvestigator(BaseInvestigator):
    "A class for determining Mac OS X Spotlight attributes of files."

    attrMap = {
        "kMDItem.*": "getkMDItem",        # generic attribute names
        "kMDItemKind": "getkMDItemKind",  # now superfluous...
    }
    
    totals = ("kMDItemDurationSeconds", "kMDItemNumberOfPages")
    # plus many others, but how to list them?

    def activate(self):
        "Try activating self, setting 'active' variable."
        
        self.active = False
        if sys.platform == "darwin":
            # self.mdDict = _parseKmdOutput(self.path)
            self.active = True
            
        return self.active
        
        
    # not well tested for structured values...
    # like above but now trying to get only the desired attribute...
    def getkMDItem(self, attrName):
        "Return any Spotlight attribute like 'kMDItemKind'."
                
        # item = self.mdDict.get(attrName, None)
        item = parseKmdOutput_single_attr(self.path, attrName)
            
        return item


    # kind of superfluous, given the generic method getkMDItem
    def getkMDItemKind(self):
        "Return Spotlight attribute 'kMDItemKind'."
        
        item = self.mdDict["kMDItemKind"]
            
        return item
