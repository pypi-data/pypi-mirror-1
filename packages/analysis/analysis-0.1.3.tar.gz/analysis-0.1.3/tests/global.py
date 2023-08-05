#!/usr/bin/env python

x = 100

def f():
    global x
    x = 123

print x
f()
print x

# vim: tabstop=4 expandtab shiftwidth=4
