#!/usr/bin/env python

# General non-tuple/list assignment does not work in CPython.

class A:
    def __iter__(self):
        return C()

class B:
    def __iter__(self):
        return D()

class C:
    def next(self):
        return 1

class D:
    def next(self):
        return "a"

a = [1, [2, 3]]
b = 3, (4, 5)
if 2:
    l = a
else:
    l = b
c, d = l
e, (f, g) = l
print e, f, g

# vim: tabstop=4 expandtab shiftwidth=4
