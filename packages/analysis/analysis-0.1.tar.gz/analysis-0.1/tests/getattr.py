#!/usr/bin/env python

class A:
    def m(self):
        pass

x = 1
a = A()
a.x = x
y = a.x
m = a.m
a.n = m
a.n()

# vim: tabstop=4 expandtab shiftwidth=4
