#!/usr/bin/env python

"""
Simple built-in classes and functions.

Copyright (C) 2005 Paul Boddie <paul@boddie.org.uk>

This software is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with this library; see the file LICENCE.txt
If not, write to the Free Software Foundation, Inc.,
59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

class boolean:
    pass

class int:
    def __add__(self, other):
        """
        NAME: int.__add__
        """
        if isinstance(other, int):
            return int()
        else:
            TypeConstraintError

    def __radd__(self, other):
        """
        NAME: int.__radd__
        """
        if isinstance(other, int):
            return int()
        else:
            TypeConstraintError

    def __sub__(self, other):
        """
        NAME: int.__sub__
        """
        if isinstance(other, int):
            return int()
        else:
            TypeConstraintError

    def __rsub__(self, other):
        """
        NAME: int.__rsub__
        """
        if isinstance(other, int):
            return int()
        else:
            TypeConstraintError

    def __lt__(self, other):
        """
        NAME: int.__lt__
        """
        return boolean()

    def __gt__(self, other):
        """
        NAME: int.__gt__
        """
        return boolean()

    def __le__(self, other):
        """
        NAME: int.__le__
        """
        return boolean()

    def __ge__(self, other):
        """
        NAME: int.__ge__
        """
        return boolean()

    def __eq__(self, other):
        """
        NAME: int.__eq__
        """
        return boolean()

    def __ne__(self, other):
        """
        NAME: int.__ne__
        """
        return boolean()

    def __len__(self):
        """
        NAME: int.__len__
        """
        return int()

class long:
    def __add__(self, other):
        """
        NAME: long.__add__
        """
        if isinstance(other, int):
            return long()
        elif isinstance(other, long):
            return long()
        else:
            TypeConstraintError

    def __radd__(self, other):
        """
        NAME: long.__radd__
        """
        if isinstance(other, int):
            return long()
        elif isinstance(other, long):
            return long()
        else:
            TypeConstraintError

    def __sub__(self, other):
        """
        NAME: long.__sub__
        """
        if isinstance(other, int):
            return long()
        elif isinstance(other, long):
            return long()
        else:
            TypeConstraintError

    def __rsub__(self, other):
        """
        NAME: long.__rsub__
        """
        if isinstance(other, int):
            return long()
        elif isinstance(other, long):
            return long()
        else:
            TypeConstraintError

    def __lt__(self, other):
        """
        NAME: long.__lt__
        """
        return boolean()

    def __gt__(self, other):
        """
        NAME: long.__gt__
        """
        return boolean()

    def __le__(self, other):
        """
        NAME: long.__le__
        """
        return boolean()

    def __ge__(self, other):
        """
        NAME: long.__ge__
        """
        return boolean()

    def __eq__(self, other):
        """
        NAME: long.__eq__
        """
        return boolean()

    def __ne__(self, other):
        """
        NAME: long.__ne__
        """
        return boolean()

    def __len__(self):
        """
        NAME: long.__len__
        """
        return int()

class float:
    def __add__(self, other):
        """
        NAME: float.__add__
        """
        if isinstance(other, int):
            return float()
        elif isinstance(other, long):
            return float()
        elif isinstance(other, float):
            return float()
        else:
            TypeConstraintError

    def __radd__(self, other):
        """
        NAME: float.__radd__
        """
        if isinstance(other, int):
            return float()
        elif isinstance(other, long):
            return float()
        elif isinstance(other, float):
            return float()
        else:
            TypeConstraintError

    def __sub__(self, other):
        """
        NAME: float.__sub__
        """
        if isinstance(other, int):
            return float()
        elif isinstance(other, long):
            return float()
        elif isinstance(other, float):
            return float()
        else:
            TypeConstraintError

    def __rsub__(self, other):
        """
        NAME: float.__rsub__
        """
        if isinstance(other, int):
            return float()
        elif isinstance(other, long):
            return float()
        elif isinstance(other, float):
            return float()
        else:
            TypeConstraintError

    def __lt__(self, other):
        """
        NAME: float.__lt__
        """
        return boolean()

    def __gt__(self, other):
        """
        NAME: float.__gt__
        """
        return boolean()

    def __le__(self, other):
        """
        NAME: float.__le__
        """
        return boolean()

    def __ge__(self, other):
        """
        NAME: float.__ge__
        """
        return boolean()

    def __eq__(self, other):
        """
        NAME: float.__eq__
        """
        return boolean()

    def __ne__(self, other):
        """
        NAME: float.__ne__
        """
        return boolean()

    def __len__(self):
        """
        NAME: float.__len__
        """
        return int()

class string:
    def __add__(self, other):
        """
        NAME: string.__add__
        """
        if isinstance(other, string):
            return string()
        else:
            TypeConstraintError

    def __radd__(self, other):
        """
        NAME: string.__radd__
        """
        if isinstance(other, string):
            return string()
        else:
            TypeConstraintError

    def __len__(self):
        """
        NAME: string.__len__
        """
        return int()

class list:
    # NOTE: __init__ not defined - special case in process_list used.
    def __getitem__(self, index):
        """
        NAME: list.__getitem__
        """
        return self.fake

    def __setitem__(self, index, value):
        """
        NAME: list.__setitem__
        """
        self.fake = value

    def __getslice__(self, start, end):
        """
        NAME: list.__getslice__
        """
        return self # NOTE: Hack to preserve illusion of immutability.

    def __setslice__(self, start, end, slice):
        """
        NAME: list.__setslice__
        """
        self.fake = slice.fake # NOTE: Hack to propagate element types.

    def append(self, value):
        """
        NAME: list.append
        """
        self.fake = value

    def __len__(self):
        """
        NAME: list.__len__
        """
        return int()

    def __add__(self, other):
        """
        NAME: list.__add__
        """
        if isinstance(other, list):
            return list()
        else:
            TypeConstraintError

    def __iter__(self):
        """
        NAME: list.__iter__
        """
        return listiterator(self)

class listiterator:
    def __init__(self, l):
        self.l = l

    def next(self):
        """
        NAME: listiterator.next
        """
        return self.l.fake

class none:
    pass

def len(x):
    return x.__len__()

def str(x):
    return x.__str__()

def isinstance(obj, cls):
    """
    NAME: isinstance
    SPECIAL
    """
    return boolean()

def issubclass(cls1, cls2):
    """
    NAME: isinstance
    SPECIAL
    """
    return boolean()

# Special values.

True = boolean()
False = boolean()
None = none()

# vim: tabstop=4 expandtab shiftwidth=4
