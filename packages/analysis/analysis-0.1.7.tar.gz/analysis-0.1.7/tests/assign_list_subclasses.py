#!/usr/bin/env python

"""
We could use this to get listiterator...

_l = []
listiterator = _l.__iter__().__class__

...but Python complains with...

TypeError: Error when calling the metaclass bases
    type 'listiterator' is not an acceptable base type
"""

class sub1(list):
    def __iter__(self):
        return sub1iterator(self)

class sub1iterator(listiterator):
    pass

class sub2(list):
    def __iter__(self):
        return sub2iterator(self)

class sub2iterator(listiterator):
    pass

a = 1
b = "1"
s1a = sub1()
s1a.append(a); s1a.append(b)
c, d = s1a
s1b = sub1()
s1b.append(c); s1b.append(d)
l = s1b
s2 = sub2()
s2.append(l); s2.append(2)
(e, f), g = s2
print a, b, c, d, e, f, g

# vim: tabstop=4 expandtab shiftwidth=4
