#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for PDF files.

This needs the 'pypdf' package to be installed for some operations.

See also: 

  http://pybrary.net/pyPdf
"""


import sys, os.path, operator, re, zlib
from os.path import dirname

try:
    import pyPdf
    HAVE_PYPDF = True
except ImportError:
    print "WARNING: Package 'pyPdf' not found."
    print "Please install from http://pybrary.net/pyPdf if you "
    print "want to use this plug-in and extract all attributes!"
    HAVE_PYPDF = False

from fileinfo.investigator import BaseInvestigator


class Record:
    pass


class PDFInvestigator(BaseInvestigator):
    "A class for determining attributes of PDF files."

    attrMap = {
        "nimgs": "getNumImages",
        "npagesizes":"getNumPdfPageSizes",
        "npageoris":"getNumPdfPageOrientations",
        # for the following 'pypdf' is needed
        "title": "getTitle",
        "author": "getAuthor",
        "producer": "getProducer",
        "creationdate": "getCreationDate",
        "npages": "getNumPdfPages",
    }

    totals = ("npages", "nimgs")

    def activate(self):
        "Try activating self, setting 'active' variable."

        try:
            self.content = file(self.path, "rb").read()
            self.active = True
        except:
            self.active = False
        
        if HAVE_PYPDF:
            self.input = pyPdf.PdfFileReader(file(self.path, "rb"))
            
        return self.active
                    

    def getNumImages(self):
        "Return the number of images of a PDF document."
        
        expr = r"\d+ +\d+ +obj.*?endobj\s+(?:%.*?[\r\n])?"
        objPat = re.compile(expr, re.M | re.S)
        items = re.findall(objPat, self.content)
        for p in [ re.compile("/%s\s*/%s" % (k, v), re.M | re.S) 
            for (k, v) in [("Type", "XObject"), ("Subtype", "Image")]]:
            items = [i for i in items if re.search(p, i) != None]

        return len(items)


    def getNumPdfPageSizes(self):
        "Return number of different page sizes in a PDF document."

        try:
            numPages = self.input.getNumPages()
            pages = [self.input.getPage(i) for i in range(numPages)]
            sizes = set([page.mediaBox.upperRight for page in pages])
            res = len(sizes)
        except:
            res = "n/a"

        return res


    def getNumPdfPageOrientations(self):
        "Return number of different page orientations in a PDF document."

        try:
            numPages = self.input.getNumPages()
            pages = [self.input.getPage(i) for i in range(numPages)]
            sizes = set([page.mediaBox.upperRight for page in pages])
            numPortrait = len([1 for (w, h) in sizes if w < h])
            numLandscape = len([1 for (w, h) in sizes if w > h])
            numSquare = len([1 for (w, h) in sizes if w == h])
            nums = 0
            if numPortrait > 0: nums += 1
            if numLandscape > 0: nums += 1
            if numSquare > 0: nums += 1
            res = nums
        except:
            res = "n/a"

        return res
        
        
    # for the following 'pypdf' is needed
    
    def getTitle(self):
        "Return the title of a PDF document."

        if not HAVE_PYPDF:
            return "n/a"

        try:
            res = self.input.getDocumentInfo().title
        except:
            res = "n/a"

        return res


    def getAuthor(self):
        "Return the author of a PDF document."

        if not HAVE_PYPDF:
            return "n/a"

        try:
            res = self.input.getDocumentInfo().author
        except:
            res = "n/a"

        return res


    def getProducer(self):
        "Return the producer of a PDF document."
        
        if not HAVE_PYPDF:
            return "n/a"

        try:
            res = self.input.getDocumentInfo().producer
            if False:
                # something like this was needed for earlier versions of PyPdf
                if res[:2] == "\xFE\xFF":
                    res = res[2:][1::2]
                elif res[:2] == "\xFF\xFE": # not tested, yet
                    res = res[2:][0::2]
        except:
            res = "n/a"

        if len(res) > 35:
            res = res[:30] + "[...]"

        return res


    def getCreationDate(self):
        "Return the creation date of a PDF document."

        if not HAVE_PYPDF:
            return "n/a"

        try:
            res = self.input.getDocumentInfo()["/CreationDate"]
        except:
            res = "n/a"

        return res


    def getNumPdfPages(self):
        "Return the number of pages in a PDF document."

        if not HAVE_PYPDF:
            return "n/a"

        try:
            res = self.input.getNumPages()
        except:
            res = "n/a"

        return res
