#!/usr/bin/env python

class A:
    def m(self):
        print "A.m", self.x
    def p(self):
        print "A.p", self.x

x = 1
a1 = A()
a1.x = x
print a1.x
y = a1.x
print y

a2 = A()
a2.x = 2
print a2.x

a1.m()
m = a1.m
m()
a2.n = m
a2.n()      # This should still print A.m 1 since the context is still a1.

a2.q = a1.p
a1.p()
a2.q()      # This should still print A.p 1 since the context is still a1.

# Test distinct references.

if 2:
    a = a1
else:
    a = a2
a.m()

# vim: tabstop=4 expandtab shiftwidth=4
