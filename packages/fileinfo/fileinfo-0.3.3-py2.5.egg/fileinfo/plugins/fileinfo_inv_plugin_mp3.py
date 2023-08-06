#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""A fileinfo plug-in for MP3 files with ID3v1.0 tags.
"""


import sys, os.path

from fileinfo.investigator import BaseInvestigator


class MP3Investigator(BaseInvestigator):
    "A class for determining ID3 tags of MP3 files."

    attrMap = {
        "artist": "getArtist",
        "album": "getAlbum",
    }

    totals = ()

    tagDataMap = {
        "title":   (  3,  33),
        "artist":  ( 33,  63),
        "album":   ( 63,  93),
        "year":    ( 93,  97),
        "comment": ( 97, 126),
        "genre":   (127, 128),
    }

    def parse(self):
        "Parse ID3v1.0 tags from a MP3 file."

        f = open(self.path, "rb", 0)
        try:
            f.seek(-128, 2)
            tagdata = f.read(128)
        finally:
            f.close()

        if tagdata[:3] == 'TAG':
            for tag, (start, end) in self.tagDataMap.items():
                data = tagdata[start:end]
                # print tag, data
                if tag == "genre":
                    self.tags[tag] = ord(data)
                else:
                    self.tags[tag] = data.replace("\00", " ").strip()


    def activate(self):
        "Try activating self, setting 'active' variable."

        self.tags = {}
        
        try:
            self.parse()
            self.active = True
        except:
            self.active = False

        return self.active


    def getArtist(self):
        "Return ID3 artist tag."

        return self.tags.get("artist", "n/a")


    def getAlbum(self):
        "Return ID3 album tag."

        return self.tags.get("album", "n/a")
