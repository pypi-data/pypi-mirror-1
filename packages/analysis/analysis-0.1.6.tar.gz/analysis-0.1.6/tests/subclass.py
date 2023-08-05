#!/usr/bin/env python

class B:

    "A base class."

    def __init__(self, x):
        self.x = x

class C(B):

    """
    A subclass of B.
    """

    def __init__(self, x):
        B.__init__(self, x)
        self.a = x + 1

b = B(1)
c = C(2)
print b.x
print c.x
print c.a

# vim: tabstop=4 expandtab shiftwidth=4
