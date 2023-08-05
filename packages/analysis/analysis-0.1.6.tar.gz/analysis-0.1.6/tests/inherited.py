#!/usr/bin/env python

class A:
    a = 123

class B(A):
    def f(self):
        print self.a

b = B()
b.f()
B.a = 234
b.f()
b.a = 345
b.f()

# vim: tabstop=4 expandtab shiftwidth=4
