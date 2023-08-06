#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"Utilities"


class groupby(dict):
    """SQL-like GROUPBY class including the logic in a Unix-like "sort | uniq".
    
    See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/259173
    """
    
    def __init__(self, seq, key=lambda x:x):
        for value in seq:
            k = key(value)
            self.setdefault(k, []).append(value)
            
    __iter__ = dict.iteritems
