#!/usr/bin/env python

if 2:
    a = "1"
    c = "1"
else:
    a = 1
    c = 1
b = (a is not None and a + 0)
print a, b
d = (c is not None or c + 0)
print c, d

# vim: tabstop=4 expandtab shiftwidth=4
