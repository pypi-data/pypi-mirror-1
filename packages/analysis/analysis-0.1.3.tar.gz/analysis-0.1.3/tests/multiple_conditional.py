#!/usr/bin/env python

def f(x):
    g(x)

def g(x):
    pass

x = 1
if x == 1:
    y = 1
else:
    y = 'a'
f(y)
y = 1.2
f(y)

# vim: tabstop=4 expandtab shiftwidth=4
