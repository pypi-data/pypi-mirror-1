#!/usr/bin/env python

def f(x):
    pass

def h(x, y):
    return x

def i():
    return "a"

a = 1
while 1:
    x = h(a, 1)
    f(x)
    a = i()

# vim: tabstop=4 expandtab shiftwidth=4
