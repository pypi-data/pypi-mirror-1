#!/usr/bin/env python

def f(x):
    pass

def h(x, y):
    return x

def i():
    return "a"

a = 1
counter = 100
while counter > 0:
    x = h(a, 1)
    f(x)
    a = i()
    counter = counter - 1

# vim: tabstop=4 expandtab shiftwidth=4
