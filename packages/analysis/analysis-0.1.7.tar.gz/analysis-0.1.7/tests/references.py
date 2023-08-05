#!/usr/bin/env python

def f(a):
    print a.x

class C:
    x = 123

f(C)
f(C())

# vim: tabstop=4 expandtab shiftwidth=4
