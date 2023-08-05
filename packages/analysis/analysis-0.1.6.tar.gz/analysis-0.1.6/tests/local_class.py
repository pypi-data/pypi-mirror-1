#!/usr/bin/env python

class C:
    w = 123
    def m(self, y):
        self.y = y
        print "C.m", C.w, self.w, self.y

def f(a, b):
    class D(C):
        x = 456
        def m(self, y):
            self.y = y
            print "D.m", C.w, self.w, D.x, self.x, self.y
    d = D()
    return d

def g(a, b):
    c = a.m
    return c(b)

def h(a):
    return a.y

d1 = f(1, 2)        # Should be an f<int, int>.D instance.
d2 = f("a", "b")    # Should be an f<str, str>.D instance.
g(d1, "1")          # Should invoke D.m(str).
g(d2, 2)            # Should invoke D.m(int).
print h(d1)         # Should return int.
print h(d2)         # Should return str.

# vim: tabstop=4 expandtab shiftwidth=4
