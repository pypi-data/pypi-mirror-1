#!/usr/bin/env python

"""
Reference classes.

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

class Reference:
    def __init__(self, class_):
        self._namespace = {}
        self._class = class_

    def __repr__(self):
        return "<Reference %s of type %s>" % (id(self), self._class.name)

# Special object creation.

def instantiate_class(class_, instantiator):
    if not hasattr(class_, "_instances"):
        class_._instances = []

    # NOTE: Only create one instance, reserving the right to make more in some
    # NOTE: more complicated arrangement.

    if len(class_._instances) == 0:
        ref = Reference(class_)
        ref.name = class_.name
        # NOTE: In a more complicated arrangement, we would distinguish between
        # NOTE: instances like this:
        #ref.name = "%s-%s" % (class_.name, len(class_._instances))
        class_._instances.append(ref)

    # Note the instantiation operation on the instantiator.

    if not hasattr(instantiator, "_instantiates"):
        instantiator._instantiates = []
    if class_ not in instantiator._instantiates:
        instantiator._instantiates.append(class_)

    return class_._instances[-1]

# vim: tabstop=4 expandtab shiftwidth=4
