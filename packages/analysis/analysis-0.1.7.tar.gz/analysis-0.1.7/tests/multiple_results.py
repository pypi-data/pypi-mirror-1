#!/usr/bin/env python

def fn(x):
    if x > 1:
        print "fn > 1"
        return (x, x-1)
    else:
        print "fn <= 1"
        return (x, None)

def fn2(x):
    a, b = x
    print a, b

a = fn(2)
print len(a)
print a
a = fn(1)
print len(a)
print a
fn2(a)

# vim: tabstop=4 expandtab shiftwidth=4
