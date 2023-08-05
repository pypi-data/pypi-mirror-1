#!/usr/bin/env python

"""
Code summaries.

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

import analysis.specialisation
import compiler
import sys

def process_module(module, path=None, stream=None):
    path = path or []
    stream = stream or sys.stdout
    print >>stream, "<html>"
    print >>stream, "<head>"
    print >>stream, "<style type='text/css'>"
    print >>stream, "div.specialisation { background-color: silver; }"
    print >>stream, "</style>"
    print >>stream, "</head>"
    print >>stream, "<body>"
    breadth_first(module, path, stream)
    print >>stream, "</body>"
    print >>stream, "</html>"

def breadth_first(node, path, stream):
    for child_node in node.getChildNodes():
        process_node(child_node, path, stream)

def process_node(node, path, stream):
    if isinstance(node, compiler.ast.Class):
        new_path = path + [node.name]
        print >>stream, "<h1>Class %s</h1>" % ".".join(new_path)
        breadth_first(node, new_path, stream)
    elif isinstance(node, compiler.ast.Function):
        new_path = path + [node.name]

        # Test for original functions.

        if hasattr(node, "_signatures"):
            print >>stream, "<h1>Function %s</h1>" % ".".join(new_path)
            print >>stream, "<table border='1'>"
            names = show_signatures_header(node._signatures, stream)
            for signature, specialisation in map(None, node._signatures, node._specialisations):
                show_signature(signature, names, specialisation, stream)
            print >>stream, "</table>"

        # Test for specialisations.

        elif hasattr(node, "_namespace"):
            print >>stream, "<div class='specialisation'>"
            print >>stream, "<h1>Function %s</h1>" % ".".join(new_path)
            print >>stream, "<table border='1'>"
            signature = analysis.specialisation.make_signature(node._namespace)
            names = show_signatures_header([signature], stream)
            show_signature(signature, names, node, stream)
            print >>stream, "</table>"
            print >>stream, "</div>"


        breadth_first(node, new_path, stream)
    else:
        breadth_first(node, path, stream)

def show_signatures_header(signatures, stream):
    names = []
    for signature in signatures:
        for name in signature.keys():
            if name not in names:
                names.append(name)
    print >>stream, "<tr>"
    print >>stream, "<th>Specialisation</th>"
    for name in names:
        print >>stream, "<th>%s</th>" % name
    print >>stream, "</tr>"
    return names

def show_signature(signature, names, specialisation, stream):
    print >>stream, "<tr>"
    print >>stream, "<th>%s</th>" % specialisation.name
    for name in names:
        print >>stream, "<td>"
        for type_name in signature.get(name, []):
            print >>stream, "%s " % type_name,
        print >>stream, "</td>"
    print >>stream, "</tr>"

# vim: tabstop=4 expandtab shiftwidth=4
