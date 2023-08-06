#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class A(object):
    # method
    def foo(self):
        "foo"
        return "foo"

class B(A):
    class C(object):
        pass

# a function
def bar():
    "bar"
    return "bar"


results = {
    "lc": 22, "nclasses": 3, "ndefs": 2, "ncomments": 4, 
    "nstrs": 11, "nkws": 8, "ndkws": 4}