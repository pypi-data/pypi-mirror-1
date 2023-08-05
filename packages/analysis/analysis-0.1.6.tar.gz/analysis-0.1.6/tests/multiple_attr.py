#!/usr/bin/env python

def f(x, v):
    x.y = v

class X:
    pass

class Y:
    pass

if 2:
    x = X()
else:
    x = Y()

x.z = 1

f(x, 3)

# vim: tabstop=4 expandtab shiftwidth=4
