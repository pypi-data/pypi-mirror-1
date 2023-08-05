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
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

--------

The docstring annotations have the following meanings:

    NAME        Indicates a "stable" name used by callers of a function instead
                of a generated name which would distinguish different
                specialisations.

    NATIVE      Means that the class or function body details are not accurate
                representations of the actual code and should not be generated
                by a compiler.

    SPECIAL     Indicates that the compiler should try and optimise calls to the
                annotated function.

--------
NATIVE
"""

class boolean:
    "NATIVE"
    def __true__(self):
        return self

class int:
    "NATIVE"
    def __add__(self, other):
        """
        NAME: builtins.int.__add__
        NATIVE
        """
        if isinstance(other, int):
            return int()
        else:
            TypeConstraintError

    def __radd__(self, other):
        """
        NAME: builtins.int.__radd__
        NATIVE
        """
        if isinstance(other, int):
            return int()
        else:
            TypeConstraintError

    def __sub__(self, other):
        """
        NAME: builtins.int.__sub__
        NATIVE
        """
        if isinstance(other, int):
            return int()
        else:
            TypeConstraintError

    def __rsub__(self, other):
        """
        NAME: builtins.int.__rsub__
        NATIVE
        """
        if isinstance(other, int):
            return int()
        else:
            TypeConstraintError

    def __lt__(self, other):
        """
        NAME: builtins.int.__lt__
        NATIVE
        """
        return boolean()

    def __gt__(self, other):
        """
        NAME: builtins.int.__gt__
        NATIVE
        """
        return boolean()

    def __le__(self, other):
        """
        NAME: builtins.int.__le__
        NATIVE
        """
        return boolean()

    def __ge__(self, other):
        """
        NAME: builtins.int.__ge__
        NATIVE
        """
        return boolean()

    def __eq__(self, other):
        """
        NAME: builtins.int.__eq__
        NATIVE
        """
        return boolean()

    def __ne__(self, other):
        """
        NAME: builtins.int.__ne__
        NATIVE
        """
        return boolean()

    def __len__(self):
        """
        NAME: builtins.int.__len__
        NATIVE
        """
        return int()

    def __str__(self):
        """
        NAME: builtins.int.__str__
        NATIVE
        """
        return string()

    def __true__(self):
        """
        NAME: builtins.int.__true__
        NATIVE
        """
        return boolean()

class long:
    "NATIVE"
    def __add__(self, other):
        """
        NAME: builtins.long.__add__
        NATIVE
        """
        if isinstance(other, int):
            return long()
        elif isinstance(other, long):
            return long()
        else:
            TypeConstraintError

    def __radd__(self, other):
        """
        NAME: builtins.long.__radd__
        NATIVE
        """
        if isinstance(other, int):
            return long()
        elif isinstance(other, long):
            return long()
        else:
            TypeConstraintError

    def __sub__(self, other):
        """
        NAME: builtins.long.__sub__
        NATIVE
        """
        if isinstance(other, int):
            return long()
        elif isinstance(other, long):
            return long()
        else:
            TypeConstraintError

    def __rsub__(self, other):
        """
        NAME: builtins.long.__rsub__
        NATIVE
        """
        if isinstance(other, int):
            return long()
        elif isinstance(other, long):
            return long()
        else:
            TypeConstraintError

    def __lt__(self, other):
        """
        NAME: builtins.long.__lt__
        NATIVE
        """
        return boolean()

    def __gt__(self, other):
        """
        NAME: builtins.long.__gt__
        NATIVE
        """
        return boolean()

    def __le__(self, other):
        """
        NAME: builtins.long.__le__
        NATIVE
        """
        return boolean()

    def __ge__(self, other):
        """
        NAME: builtins.long.__ge__
        NATIVE
        """
        return boolean()

    def __eq__(self, other):
        """
        NAME: builtins.long.__eq__
        NATIVE
        """
        return boolean()

    def __ne__(self, other):
        """
        NAME: builtins.long.__ne__
        NATIVE
        """
        return boolean()

    def __len__(self):
        """
        NAME: builtins.long.__len__
        NATIVE
        """
        return int()

    def __str__(self):
        """
        NAME: builtins.long.__str__
        NATIVE
        """
        return string()

    def __true__(self):
        """
        NAME: builtins.int.__true__
        NATIVE
        """
        return boolean()

class float:
    "NATIVE"
    def __add__(self, other):
        """
        NAME: builtins.float.__add__
        NATIVE
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
        NAME: builtins.float.__radd__
        NATIVE
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
        NAME: builtins.float.__sub__
        NATIVE
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
        NAME: builtins.float.__rsub__
        NATIVE
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
        NAME: builtins.float.__lt__
        NATIVE
        """
        return boolean()

    def __gt__(self, other):
        """
        NAME: builtins.float.__gt__
        NATIVE
        """
        return boolean()

    def __le__(self, other):
        """
        NAME: builtins.float.__le__
        NATIVE
        """
        return boolean()

    def __ge__(self, other):
        """
        NAME: builtins.float.__ge__
        NATIVE
        """
        return boolean()

    def __eq__(self, other):
        """
        NAME: builtins.float.__eq__
        NATIVE
        """
        return boolean()

    def __ne__(self, other):
        """
        NAME: builtins.float.__ne__
        NATIVE
        """
        return boolean()

    def __len__(self):
        """
        NAME: builtins.float.__len__
        NATIVE
        """
        return int()

    def __str__(self):
        """
        NAME: builtins.float.__str__
        NATIVE
        """
        return string()

    def __true__(self):
        """
        NAME: builtins.int.__true__
        NATIVE
        """
        return boolean()

class string:
    "NATIVE"
    def __add__(self, other):
        """
        NAME: builtins.string.__add__
        NATIVE
        """
        if isinstance(other, string):
            return string()
        else:
            TypeConstraintError

    def __radd__(self, other):
        """
        NAME: builtins.string.__radd__
        NATIVE
        """
        if isinstance(other, string):
            return string()
        else:
            TypeConstraintError

    def __len__(self):
        """
        NAME: builtins.string.__len__
        NATIVE
        """
        return int()

    def __str__(self):
        return self

    def __true__(self):
        return self.__len__() != 0

class list:
    "NATIVE"
    # NOTE: __init__ not defined - special case in visitList used.
    def __getitem__(self, index):
        """
        NAME: builtins.list.__getitem__
        NATIVE
        """
        return self.fake

    def __setitem__(self, index, value):
        """
        NAME: builtins.list.__setitem__
        NATIVE
        """
        self.fake = value

    def __getslice__(self, start, end):
        """
        NAME: builtins.list.__getslice__
        NATIVE
        """
        return self # NOTE: Hack to preserve illusion of immutability.

    def __setslice__(self, start, end, slice):
        """
        NAME: builtins.list.__setslice__
        NATIVE
        """
        self.fake = slice.fake # NOTE: Hack to propagate element types.

    def append(self, value):
        """
        NAME: builtins.list.append
        NATIVE
        """
        self.fake = value

    def __len__(self):
        """
        NAME: builtins.list.__len__
        NATIVE
        """
        return int()

    def __add__(self, other):
        """
        NAME: builtins.list.__add__
        NATIVE
        """
        if isinstance(other, list):
            return list()
        else:
            TypeConstraintError

    def __str__(self):
        """
        NAME: builtins.list.__str__
        NATIVE
        """
        return string()

    def __iter__(self):
        """
        NAME: builtins.list.__iter__
        """
        return listiterator(self)

    def __true__(self):
        return self.__len__() != 0

class listiterator:
    "NATIVE"

    def __init__(self, l):
        """
        NAME: builtins.listiterator.__init__
        NATIVE
        """
        self.l = l

    def next(self):
        """
        NAME: builtins.listiterator.next
        NATIVE
        """
        return self.l.fake

    def __true__(self):
        """
        NAME: builtins.int.__true__
        NATIVE
        """
        return boolean()

class tuple:
    "NATIVE"
    # NOTE: __init__ not defined - special case in visitTuple used.
    def __getitem__(self, index):
        """
        NAME: builtins.tuple.__getitem__
        NATIVE
        """
        return self.fake

    def __getslice__(self, start, end):
        """
        NAME: builtins.tuple.__getslice__
        NATIVE
        """
        return self # NOTE: Hack to preserve illusion of immutability.

    def append(self, value):
        """
        NAME: builtins.tuple.append
        NATIVE
        """
        self.fake = value

    def __len__(self):
        """
        NAME: builtins.tuple.__len__
        NATIVE
        """
        return int()

    def __add__(self, other):
        """
        NAME: builtins.tuple.__add__
        NATIVE
        """
        if isinstance(other, tuple):
            return tuple()
        else:
            TypeConstraintError

    def __str__(self):
        """
        NAME: builtins.tuple.__str__
        NATIVE
        """
        return string()

    def __iter__(self):
        """
        NAME: builtins.tuple.__iter__
        """
        return tupleiterator(self)

    def __true__(self):
        return self.__len__() != 0

class tupleiterator:
    "NATIVE"

    def __init__(self, l):
        """
        NAME: builtins.tupleiterator.__init__
        NATIVE
        """
        self.l = l

    def next(self):
        """
        NAME: builtins.tupleiterator.next
        NATIVE
        """
        return self.l.fake

    def __true__(self):
        """
        NAME: builtins.int.__true__
        NATIVE
        """
        return boolean()

class none:
    "NATIVE"
    pass

def isinstance(obj, cls):
    """
    NAME: builtins.isinstance
    NATIVE
    SPECIAL
    """
    return boolean()

def issubclass(cls1, cls2):
    """
    NAME: builtins.isinstance
    NATIVE
    SPECIAL
    """
    return boolean()

def len(x):
    return x.__len__()

def str(x):
    return x.__str__()

# Special values. None of these definitions should be generated by the compiler.
# All such definitions should be made in the underlying implementation.

True = boolean()
False = boolean()
None = none()

# Special functions. These all operate on references at run-time.

def __is__(a, b):
    """
    NAME: builtins.__is__
    NATIVE
    """
    return boolean()

def __is_not__(a, b):
    """
    NAME: builtins.__is_not__
    NATIVE
    """
    return boolean()

def __not__(a):
    """
    NAME: builtins.__not__
    NATIVE
    """
    return boolean()

# vim: tabstop=4 expandtab shiftwidth=4
