#!/usr/bin/env python

class X:
    def m(self):
        print "X.m"

class Y:
    def m(self):
        print "Y.m"

if 2:
    x = X()
else:
    x = Y()

x.m()

# vim: tabstop=4 expandtab shiftwidth=4
