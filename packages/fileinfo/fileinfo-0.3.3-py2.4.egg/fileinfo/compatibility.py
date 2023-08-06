#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"Utilities"

# handle missing built-in set
try:
    s = set((1,))
except NameError:
    # Python 2.3
    from sets import Set as set

