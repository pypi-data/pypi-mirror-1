#!/usr/bin/env python

"""
Namespace handling.

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
"""

import compiler
import analysis.node

class ScopeError(Exception):
    pass

class NamespaceRegister:

    "A name register for a given namespace."

    def __init__(self, locals, globals, builtins, name_qualifier=None,
        name_context=None):

        """
        Initialise the register with the given 'locals', 'globals' and
        'builtins' namespaces.
        The optional 'name_qualifier' is used to qualify certain names.
        The optional 'name_context' is used to indicate the kind of local
        scope encapsulated by this namespace.
        """

        self.locals = locals
        self.globals = globals
        self.builtins = builtins
        self.name_qualifier = name_qualifier
        self.name_context = name_context
        self.return_nodes = []
        self.blocked_nodes = []
        self.global_names = []

    def load(self, node):

        "Find the name associated with the given 'node' in a namespace."

        analysis.node.reset(node)
        found_nodes, scope = self._load_name(node.name)
        for found_node in found_nodes:
            analysis.node.link(node, found_node, overwrite=0)

        if hasattr(node, "_scope") and node._scope != scope:
            raise ScopeError, node

        node._scope = scope
        node._name_context = self.name_context
        node._qualified_name = self.get_qualified_name(node.name)

    def _load_name(self, name):

        """
        Find the 'name' in the namespace hierarchy, returning a list of
        definitions corresponding to that name in the most local namespace
        possible, along with a scope identifier indicating in which scope the
        definitions were found.
        """

        for namespace, scope in [(self.locals, "locals"), (self.globals, "globals"), (self.builtins, "builtins")]:
            if namespace.has_key(name):
                return namespace[name], scope

        raise UnboundLocalError, name

    def store(self, node):

        """
        Store the name associated with the given 'node' in the local namespace.
        """

        if node.name in self.global_names:
            self.globals[node.name] = [node]
            scope = "globals"
        else:
            self.locals[node.name] = [node]
            scope = "locals"

        if hasattr(node, "_scope") and node._scope != scope:
            raise ScopeError, node

        node._scope = scope
        node._name_context = self.name_context
        node._qualified_name = self.get_qualified_name(node.name)

    def make_global(self, node):

        """
        Remove the name associated with the given 'node' in the local namespace.
        This is used when establishing global usage.
        """

        for name in node.names:
            if self.locals.has_key(name):
                del self.locals[name]
            self.globals[name] = [node]
            if name not in self.global_names:
                self.global_names.append(name)

    def return_node(self, node):
        self.return_nodes.append(node)

    def add_blocked_node(self, node):
        self.blocked_nodes.append(node)

    def get_qualified_name(self, name):
        if self.name_qualifier:
            return self.name_qualifier + "." + name
        else:
            return name

def get_locals_layout(node, include_parameters=1):

    """
    Return a list of tuples of the form (name, definition-nodes) indicating the
    layout of parameter and local variable definitions for the given function
    (or other namespace-bearing) 'node'.
    """

    if hasattr(node, "argnames"):
        argnames = list(node.argnames[:])
    else:
        argnames = []

    locals = []
    names = node._namespace.keys()
    names.sort()
    for name in names:
        if name not in argnames or include_parameters:
            locals.append((name, node._namespace[name]))
    return locals

# vim: tabstop=4 expandtab shiftwidth=4
