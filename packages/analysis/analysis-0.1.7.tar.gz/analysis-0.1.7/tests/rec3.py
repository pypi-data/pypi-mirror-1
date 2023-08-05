#!/usr/bin/env python

def f(x):
    if len(x) == 1:
        return x[0]
    else:
        return f(x[1:])

print f([1,2,3])
print f(["a", "b", "c"])

# vim: tabstop=4 expandtab shiftwidth=4
