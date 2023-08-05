#!/usr/bin/env python

class my_int(int):
    pass

x = 1

if isinstance(x, int):      # Can be deduced.
    y = 1
    a = x                   # Should be int.
else:
    y = 0

print x, y, a

if isinstance(1, int):      # Can be deduced.
    z = 1
else:
    z = 0

print z

l = [1, 1.2]
if isinstance(l[0], int):   # Cannot generally be deduced.
    p = 1
    b = l[0]                # Should be int, float.
else:
    p = 0
    c = l[0]                # Should be int, float.

print p, b

x2 = my_int()

if isinstance(x2, my_int):  # Can be deduced.
    y2 = 1
    a2 = x2                 # Should be my_int.
else:
    y2 = 0
    b2 = x2                 # Should be unreachable.

print y2

if isinstance(x2, int):     # Can be deduced.
    y3 = 1
    a3 = x2                 # Should be my_int.
else:
    y3 = 0
    b3 = x2                 # Should be unreachable.

print y3

if isinstance(x2, float):   # Can be deduced.
    y4 = 1
    a4 = x2                 # Should be unreachable.
else:
    y4 = 0
    b4 = x2                 # Should be my_int.

print y4

# vim: tabstop=4 expandtab shiftwidth=4
