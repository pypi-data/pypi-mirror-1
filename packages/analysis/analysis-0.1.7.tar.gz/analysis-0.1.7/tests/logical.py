#!/usr/bin/env python

for a in (0, 1, 2, "", "a"):
    for b in (0, 1, 2, "", "a"):
        c = a and b
        d = not (a and b)
        e = a or b
        print a, b, c, d, e
    f = not a
    print f

# vim: tabstop=4 expandtab shiftwidth=4
