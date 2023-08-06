#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def foo(arg):
    return foo

def bar(*args):
    return bar

class C(object):
    def meth(self, arg):
        return arg
    
class FooBar(object):
    @foo
    def foo(self):
        return "foo"

c = C()

@c.meth
@foo
@bar(1, 2)
def foobar(arg):
    return "bar"
