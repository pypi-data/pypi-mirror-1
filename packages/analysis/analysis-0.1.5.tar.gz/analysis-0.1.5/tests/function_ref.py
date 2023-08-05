#!/usr/bin/env python

def f(a):
    print "f", a

def g(a):
    print "g", a

x = f
x(1)
if 1:
    x = g
x(1)

# vim: tabstop=4 expandtab shiftwidth=4
