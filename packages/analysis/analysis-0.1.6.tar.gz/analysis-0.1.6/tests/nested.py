#!/usr/bin/env python

def f(x):
    if not isinstance(x, list):
        return g(x)
    else:
        return f(x[0])

def g(x):
    #return x + x
    return x

print f([[[1]]])
print f([[["a"]]])

# vim: tabstop=4 expandtab shiftwidth=4
