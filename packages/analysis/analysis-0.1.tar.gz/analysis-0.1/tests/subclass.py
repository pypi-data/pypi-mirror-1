#!/usr/bin/env python

class B:
    def __init__(self, x):
        self.x = x

class C:
    def __init__(self, x):
        B.__init__(self, x)
        self.a = x

b = B(1)
c = C(2)

# vim: tabstop=4 expandtab shiftwidth=4
