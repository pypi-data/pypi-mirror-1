#!/usr/bin/env python

"""
Utility functions for output.

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

import compiler, os
import analysis.source
from analysis.output.visitors.C import CVisitor
from analysis.output.visitors.HTML import HTMLVisitor
from analysis.output.generators.common import RawGenerator

def generate(m, stream, visitor):

    """
    Generate output for the module 'm', sending program definitions to the given
    'stream', using the given 'visitor' class.
    """

    v = visitor(RawGenerator(stream))
    compiler.walk(m, v, v)
    stream.close()

def generate_file(m, filename, visitor):

    """
    Generate output for the module 'm', sending program definitions to the file
    with the given 'filename', using the given 'visitor' class.
    """

    stream = open(filename, "w")
    generate(m, stream, visitor)
    stream.close()

def generate_sources(m, filename, builtins_filename):

    """
    Generate output for the module 'm', sending program definitions to the file
    with the given 'filename', and sending built-in declarations to the file
    with the given 'builtins_filename'.
    """

    generate_file(analysis.source.builtins, builtins_filename, CVisitor)
    generate_file(m, filename, CVisitor)

def generate_doc(m, filename):

    """
    Generate output for the module 'm', sending program definitions to the file
    with the given 'filename'.
    """

    generate_file(m, filename, HTMLVisitor)

# vim: tabstop=4 expandtab shiftwidth=4
