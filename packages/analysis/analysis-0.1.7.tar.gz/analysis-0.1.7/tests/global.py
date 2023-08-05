#!/usr/bin/env python

x = 100

class Y:
    pass

y = Y()
y.a = 12

def f():
    global x
    print x
    x = 123
    global y
    print y.a
    y.a = 1234

print x
print y.a
f()
print x
print y.a

# vim: tabstop=4 expandtab shiftwidth=4
