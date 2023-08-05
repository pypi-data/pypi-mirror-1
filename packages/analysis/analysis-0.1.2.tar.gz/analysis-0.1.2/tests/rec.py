#!/usr/bin/env python

def f(x):
    print x
    if x <= 0:
        return 0
    else:
        return f(x - 1)

print f(3)

# vim: tabstop=4 expandtab shiftwidth=4
