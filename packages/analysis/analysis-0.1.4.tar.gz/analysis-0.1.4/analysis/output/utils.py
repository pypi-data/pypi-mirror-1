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
59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

import compiler, os
import analysis.utils
from analysis.output.visitors.C import CVisitor
from analysis.output.generators.common import RawGenerator

def generate(m, stream, builtins_stream):

    """
    Generate output for the module 'm', sending program definitions to the given
    'stream', and sending built-in declarations to the given 'builtins_stream'.
    """

    v = CVisitor(RawGenerator(builtins_stream))
    compiler.walk(analysis.utils.builtins, v, v)
    builtins_stream.close()

    v = CVisitor(RawGenerator(stream))
    compiler.walk(m, v, v)
    stream.close()

def generate_files(m, filename, builtins_filename):

    """
    Generate output for the module 'm', sending program definitions to the file
    with the given 'filename', and sending built-in declarations to the file
    with the given 'builtins_filename'.
    """

    stream = open(filename, "w")
    builtins_stream = open(builtins_filename, "w")
    generate(m, stream, builtins_stream)
    stream.close()
    builtins_stream.close()

# vim: tabstop=4 expandtab shiftwidth=4
