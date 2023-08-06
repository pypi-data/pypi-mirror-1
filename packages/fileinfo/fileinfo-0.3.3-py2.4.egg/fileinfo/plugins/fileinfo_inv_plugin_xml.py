#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for XML files.
"""


import sys, os.path, compiler, tokenize, cStringIO, keyword
from xml.sax.handler import ContentHandler
import xml.sax

from fileinfo.investigator import BaseInvestigator


class CountHandler(ContentHandler):
    "A SAX content handler."
    
    def __init__(self):
        self.currDepth = 0
        self.maxDepth = 0
        self.tags = {}
        self.attrNames = []


    def startElement(self, name, attrs):
        "Handle start of element."
        
        self.currDepth = self.currDepth + 1
        self.maxDepth = max(self.maxDepth, self.currDepth)
        
        #if not self.tags.has_key(name):
        #    self.tags[name] = 0
        #self.tags[name] += 1
        self.tags[name] = 1 + self.tags.get(name, 0)
        
        attrNames = attrs.getNames()
        if attrNames:
            self.attrNames += attrNames


    def endElement(self, name):
        "Handle end of element."
        
        self.currDepth = self.currDepth - 1


class XMLInvestigator(BaseInvestigator):
    "A class for determining attributes of XML files."

    attrMap = {
        "depth": "getDepth",
        "ntags": "getNumTags",
        "ndtags": "getNumDiffTags",
        "nattrs": "getNumAttrs",
        "ndattrs": "getNumDiffAttrs",
    }

    totals = ("ntags", "nattrs")

        
    def activate(self):
        "Try activating self, setting 'active' variable."
        
        try:
            self.parser = xml.sax.make_parser()
            self.handler = CountHandler()
            self.parser.setContentHandler(self.handler)

            self.active = True
        except:
            self.active = False

        return self.active


    def getDepth(self):
        "Return max. depth of XML tags."

        self.parser.parse(self.path)        

        return self.handler.maxDepth


    def getNumTags(self):
        "Return number of XML tags."

        self.parser.parse(self.path)        
        tagDict = self.handler.tags
        ntags = sum([v for (k, v) in tagDict.items()])

        return ntags


    def getNumDiffTags(self):
        "Return number of different XML tags."

        self.parser.parse(self.path)        
        tagDict = self.handler.tags
        tags = [v for (k, v) in tagDict.items()]

        return len(set(tags))


    def getNumAttrs(self):
        "Return number of XML tag attributes."

        self.parser.parse(self.path)        
        nattrs = len(self.handler.attrNames)

        return nattrs


    def getNumDiffAttrs(self):
        "Return number of different XML tag attributes."

        self.parser.parse(self.path)        
        attrs = self.handler.attrNames

        return len(set(attrs))
