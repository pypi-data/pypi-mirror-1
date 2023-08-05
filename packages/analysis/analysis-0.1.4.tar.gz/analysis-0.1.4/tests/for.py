#!/usr/bin/env python

for i in [1, 2, 3]:
    print i

for a, b in [[1, 2], [3, 4]]:
    print a, b

for c in [[], ["a", "b", "c"], ["d", "e", "f", "g"], ["h"]]:
    print "List:"
    for d in c:
        print d

# vim: tabstop=4 expandtab shiftwidth=4
