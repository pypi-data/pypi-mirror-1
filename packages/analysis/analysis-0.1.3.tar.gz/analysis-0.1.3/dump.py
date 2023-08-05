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
59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

import compiler
import analysis.utils
import analysis.output.utils
from analysis.output.generators.common import AbstractGenerator
from analysis.output.generators.cpu6502 import CPU6502Generator
from analysis.output.visitors.instruction import InstructionVisitor
import sys
import os

debug = ("--debug" in sys.argv)

if len(sys.argv) < 2:
    print "Syntax:", sys.argv[0], "<filename> [--C] [-O <output-filename>]"
    print "  --C    Generate C programming language code."
    sys.exit(1)

m = analysis.utils.process_file(sys.argv[1], debug=debug)
if "-O" in sys.argv:
    opt = sys.argv.index("-O")
    stream = open(sys.argv[opt + 1], "w")
else:
    stream = sys.stdout

# C programming language generation.

if "--C" in sys.argv:
    builtins_stream = open(os.path.join("tools", "C", "builtins.h"), "w")
    analysis.output.utils.generate(m, stream, builtins_stream)

# Experimental/diagnostic assembly language generation.

else:
    if "--6502" in sys.argv:
        g = CPU6502Generator(stream)
    else:
        g = AbstractGenerator(stream)

    v = InstructionVisitor(g)
    g.start_of_code()
    compiler.walk(m, v, v)
    g.end_of_code()

# vim: tabstop=4 expandtab shiftwidth=4
