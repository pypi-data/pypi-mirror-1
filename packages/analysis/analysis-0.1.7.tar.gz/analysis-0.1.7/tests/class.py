#!/usr/bin/env python

class B:
    def __init__(self, x):
        self.x = x

class C:
    x = 42
    #y = [1,2,3]
    b1 = B(1)
    b2 = B("a")

class D(C):
    pass

C.x = 43
C.b1.x = 2
print C.x
print C.b1.x
print C.b2.x
#c = B
#print c.x
c = C
print c.x
if 1 == 2:
    c = D
print c.x
d = c()
dc = d.__class__
print dc.x

# vim: tabstop=4 expandtab shiftwidth=4
