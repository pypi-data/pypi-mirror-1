#!/usr/bin/env python

"""
Dump a program's instructions.

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
import analysis.source
import analysis.output.utils
from analysis.output.generators.common import AbstractGenerator
from analysis.output.generators.cpu6502 import CPU6502Generator
from analysis.output.visitors.instruction import InstructionVisitor
import sys
import os

debug = ("--debug" in sys.argv)

if len(sys.argv) < 2:
    print "Syntax:", sys.argv[0], "<filename> [--C <builtins-output-filename> | --HTML] <output-filename>"
    print "  --C    Generate C programming language code."
    print "  --HTML Generate HTML summary."
    sys.exit(1)

m = analysis.source.process_file(sys.argv[1], debug=debug)
filename = sys.argv[-1]

# C programming language generation.

if "--C" in sys.argv:
    builtins_filename = sys.argv[-2]
    analysis.output.utils.generate_sources(m, filename, builtins_filename)

# HTML summary.

elif "--HTML" in sys.argv:
    analysis.output.utils.generate_doc(m, filename)

# Experimental/diagnostic assembly language generation.

else:
    stream = open(filename, "w")

    if "--6502" in sys.argv:
        g = CPU6502Generator(stream)
    else:
        g = AbstractGenerator(stream)

    v = InstructionVisitor(g)
    g.start_of_code()
    compiler.walk(m, v, v)
    g.end_of_code()

    stream.close()

# vim: tabstop=4 expandtab shiftwidth=4
