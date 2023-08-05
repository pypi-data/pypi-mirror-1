#!/usr/bin/env python

"""
Utility functions.

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

import compiler, os
import analysis.source

builtins = None
current_filename = None

def process_builtins(debug=0):
    global builtins
    if builtins is None:
        builtins = compiler.parseFile(os.path.join("analysis", "builtins.py"))
        visitor = analysis.source.AnalysisVisitor(debug=debug)
        compiler.walk(builtins, visitor, visitor)

def process(s, debug=0):
    process_builtins(debug=debug)
    module = compiler.parse(s)
    visitor = analysis.source.AnalysisVisitor(builtins._namespace, debug=debug)
    compiler.walk(module, visitor, visitor)
    return module

def process_file(filename, debug=0):
    process_builtins(debug=debug)

    # Set the filename in this module because set_filename only works on
    # completed trees.

    global current_filename
    current_filename = filename

    module = compiler.parseFile(filename)
    visitor = analysis.source.AnalysisVisitor(builtins._namespace, get_module_name(filename), debug=debug)
    compiler.walk(module, visitor, visitor)

    # Set the filename on the completed tree.

    compiler.misc.set_filename(filename, module)
    return module

def prompt():
    try:
        lines = []
        while 1:
            lines.append(raw_input(">>>> "))
    except EOFError:
        pass
    return process("\n".join(lines))

def get_module_name(filename):
    parts = []
    head, ext = os.path.splitext(filename)
    while head:
        head, tail = os.path.split(head)
        parts.insert(0, tail)
    return ".".join(parts)

def get_line(node):
    if hasattr(node, "filename"):
        filename = node.filename
    else:
        filename = current_filename

    if filename is None:
        return ""

    f = open(filename)
    lines = f.readlines()
    f.close()
    return lines[node.lineno - 1]

# vim: tabstop=4 expandtab shiftwidth=4
