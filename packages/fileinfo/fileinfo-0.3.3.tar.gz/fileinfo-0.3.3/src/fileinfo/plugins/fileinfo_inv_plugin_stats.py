#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for general file attributes.
"""


from fileinfo.investigator import BaseInvestigator


class StatInvestigator(BaseInvestigator):
    "A class for determining general attributes of files."

    attrMap = {
        "counter": "counter",
        "lc": "getLineCount",
        "wc": "getWordCount",
        "md5": "getMd5Hash",
    }

    totals = ("lc", "wc")

    def __init__(self, path):
        self.path = path
        self.cnt = -1

                
    def activate(self):
        "Try activating self, setting 'active' variable."
        
        self.active = True
        self.content = None
        return self.active
        
        
    def counter(self):
        "A counter generator."
        
        # kind of dummy code
        self.cnt += 1
        return self.cnt


    def getLineCount(self):
        "Return the number of lines in a file."
    
        if self.content is None:
            self.content = open(self.path).read()
        content = getattr(self, "content", self.content)

        return content.count("\n") + int(len(content) > 0)
        
    
    def getWordCount(self):
        "Return the number of words in a file."
        
        if self.content is None:
            self.content = open(self.path).read()
        content = getattr(self, "content", self.content)

        return len(content.split())


    def getMd5Hash(self):
        "Return the MD5 hash value of an entire file."
        
        import md5
        if self.content is None:
            self.content = open(self.path).read()
        content = getattr(self, "content", self.content)
        m = md5.new()
        m.update(content)
        hash = m.hexdigest()
        
        return hash
