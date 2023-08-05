#!/usr/bin/env python

"""
Creation and retrieval of specialisations.

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

import copy
from analysis.common import *

def get_specialisation(block, signature):

    """
    Return a specialisation for the given 'block' having the given 'signature'.
    If no existing specialisation exists, create a new one.
    """

    if hasattr(block, "_specialisations") and signature in block._signatures:
        return block._specialisations[block._signatures.index(signature)]
    else:
        return create_specialisation(block, signature)

def has_specialisation(block, signature):

    """
    Return whether the given 'block' has a specialisation with the given
    'signature'.
    """

    return hasattr(block, "_specialisations") and signature in block._signatures

def create_specialisation(block, signature):

    """
    For the specified 'block', create a new specialisation with the given
    'signature'.
    """

    specialisation = deepcopy(block)

    if not hasattr(block, "_specialisations"):
        block._specialisations = []
        block._signatures = []

    block._specialisations.append(specialisation)
    block._signatures.append(signature)

    # Define the name and the original block.

    if hasattr(block, "name"):
        specialisation.name = "%s___%s" % (block.name, len(block._specialisations))
        specialisation._qualified_name = "%s___%s" % (block._qualified_name, len(block._specialisations))
    else:
        specialisation.name = "block___%s" % len(block._specialisations)
        specialisation._qualified_name = "block___%s" % len(block._specialisations)

    # Remove the parent reference (used by call_specialisation to determine
    # whether the specialisation is new).

    delattr(specialisation, "_parent")

    # Mark the specialisation as such.

    specialisation._specialisation = 1

    return specialisation

def make_signature(ns):

    """
    Make a signature given the namespace 'ns' using reference names.
    """

    signature = {}
    for name, nodes in ns.items():
        signature[name] = []
        for node in nodes:
            defs = []

            # lobj used to support function references.

            for node_type in lobj(node):
                defs.append(node_type.name)
            signature[name] = defs
    return signature

def deepcopy(obj):
    protected = ["_parent", "_globals", "_specialisations", "_signatures"]
    new_obj = copy.copy(obj)
    if hasattr(new_obj, "__dict__"):
        for name, value in new_obj.__dict__.items():
            if name not in protected:
                setattr(new_obj, name, deepcopy(getattr(new_obj, name)))
        new_obj._original = obj
    elif type(new_obj) == type([]):
        for i in range(0, len(new_obj)):
            new_obj[i] = deepcopy(new_obj[i])
    return new_obj

# vim: tabstop=4 expandtab shiftwidth=4
