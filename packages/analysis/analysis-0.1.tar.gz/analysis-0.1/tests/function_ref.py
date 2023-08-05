#!/usr/bin/env python

def f(a):
    pass

def g(a):
    pass

x = f
x(1)
if 2:
    x = g
x(1)

# vim: tabstop=4 expandtab shiftwidth=4
