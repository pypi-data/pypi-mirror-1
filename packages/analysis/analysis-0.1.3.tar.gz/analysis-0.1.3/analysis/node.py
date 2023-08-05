#!/usr/bin/env python

"""
Node manipulations.

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

import sys

class BlockedError(Exception):
    pass

def reset(node):
    node._contexts = {}

def link(target, source, blocking=0, overwrite=1):

    """
    Link between 'target' and 'source'.

    If the optional 'blocking' parameter is set to a true value, raise an
    exception if 'source' has no contexts defined. Otherwise, where no contexts
    are defined, introduce the 'source' as a context item.

    If the optional 'overwrite' is set to a false value, the 'target' node's
    contexts will be merged with those from the 'source' node. Otherwise, the
    'target' node's contexts will be overwritten.
    """

    if hasattr(source, "_contexts"):
        context_items = source._contexts.items()
    else:
        if blocking:
            raise BlockedError, (target, source)
        else:
            context_items = [(None, [source])]
    _copy_contexts(target, context_items, overwrite=overwrite)

def merge(target, source, blocking=0):

    """
    Link between 'target' and 'source', copying the contexts of 'source'
    into 'target'.

    If the optional 'blocking' parameter is set to a true value, raise an
    exception if 'source' has no contexts defined. Otherwise, where no contexts
    are defined, none are copied to 'target'.
    """

    if hasattr(source, "_contexts"):
        context_items = source._contexts.items()
    else:
        if blocking:
            raise BlockedError, (target, source)
        else:
            context_items = []
    _copy_contexts(target, context_items, overwrite=0)

def _copy_contexts(target, context_items, overwrite):
    if not hasattr(target, "_contexts"):
        target._contexts = {}
    for key, values in context_items:
        if overwrite:
            target._contexts[key] = values
        else:
            if not target._contexts.has_key(key):
                target._contexts[key] = []
            for value in values:
                if value not in target._contexts[key]:
                    target._contexts[key].append(value)

# vim: tabstop=4 expandtab shiftwidth=4
