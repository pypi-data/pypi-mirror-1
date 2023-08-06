#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"module doc" " continued module doc"

"not a module doc"


class MyClass(object):
    "class doc"

    def foo(self):
        "method doc"    
        return "foo"


def bar():
    # comment 1
    "function doc" # comment 2
    return "bar"


class MyClass1(object):
    "class doc 1"

    def foo(self):
        "method doc" " continued method doc"
        return "foo"


def bar1():
    x = 1
    "not a function doc"
    return "bar1"


def bar2():
    """multi-line 
    function doc"""
    return "bar2"


if True:
    "not a docstring"
    x = 1