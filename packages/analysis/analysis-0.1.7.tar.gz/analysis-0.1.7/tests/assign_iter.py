#!/usr/bin/env python

# General non-tuple/list assignment does not work in CPython.

class A:
    def __init__(self, value, size):
        self.value = value
        self.size = size

    def __iter__(self):
        return C(self.value, self.size)

class C:
    def __init__(self, value, size):
        self.value = value
        self.size = size

    def next(self):
        if self.size > 0:
            self.size -= 1
            return self.value
        else:
            raise StopIteration() # NOTE: Make this compliant with Python.

a = [1, [2, 3]]
b = 3, (4, 5)
if 2:
    l = a
else:
    l = b
c, d = l
e, (f, g) = l
print e, f, g

a2 = A(1, 2)
b2 = A("a", 2)
if 2:
    l2 = a2
else:
    l2 = b2
c2, d2 = l2
print c2, d2

# vim: tabstop=4 expandtab shiftwidth=4
