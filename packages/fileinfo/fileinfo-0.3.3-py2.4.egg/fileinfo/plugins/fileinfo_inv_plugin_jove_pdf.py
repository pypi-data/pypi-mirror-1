#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for accessing the JHOVE file validator.

You need to set the variable 'jhoveHome' to the path of the JHOVE 
installation directory on your system, if you want to use this 
plug-in. This is very experimental...

See also: 

  http://hul.harvard.edu/jhove
"""


import re
import sys, os.path
from os import popen

from fileinfo.investigator import BaseInvestigator


jhoveHome = "/Applications/Added/jhove"


class JhovePdfInvestigator(BaseInvestigator):
    "A class for validating PDF files using Jhove."

    attrMap = {
        "status": "getstatus",
        "errmsg": "geterrmsg",
        "errmsgext": "geterrmsgext",
    }

    totals = ()

        
    def activate(self):
        "Try activating self, setting 'active' variable."
        
        if os.path.exists(jhoveHome):
            format = "%s/jhove -c %s/conf/jhove.conf -m pdf-hul -k %s" 
            cmd = format % (jhoveHome, jhoveHome, self.path)
            self.jhoveOutput = popen(cmd).read()
            
            self.active = True
        else:
            self.active = False

        return self.active


    def getstatus(self):
        "Return Jhove status."

        # format = "%s/jhove -c %s/conf/jhove.conf -m pdf-hul -k %s" 
        # cmd = format % (jhoveHome, jhoveHome, self.path)
        # output = popen(cmd).read()
        m = re.search("^\s*Status:\s*(.*)$", self.jhoveOutput, re.M)
        if m:
            output = m.groups()[0]
        else:
            output = "n/a"
        return output


    def geterrmsg(self):
        "Return Jhove error message."

        # format = "%s/jhove -c %s/conf/jhove.conf -m pdf-hul -k %s" 
        # cmd = format % (jhoveHome, jhoveHome, self.path)
        # output = popen(cmd).read()
        m = re.search("^\s*ErrorMessage:\s*(.*)$", self.jhoveOutput, re.M)
        if m:
            output = m.groups()[0]
        else:
            output = "n/a"
        return output


    def geterrmsgext(self):
        "Return Jhove extended error message."

        # format = "%s/jhove -c %s/conf/jhove.conf -m pdf-hul -k %s" 
        # cmd = format % (jhoveHome, jhoveHome, self.path)
        # output = popen(cmd).read()
        m = re.search("^\s* ErrorMessage:\s*([\w ]+)\s+(Offset:\s+\d+)$", self.jhoveOutput, re.M)
        if m:
            output = "%s (%s)" % m.groups()
        else:
            m = re.search("^\s*ErrorMessage:\s*(.*)$", self.jhoveOutput, re.M)
            if m:
                output = m.groups()[0]
            else:
                output = "n/a"
        return output.replace("dictionary", "dict.")
