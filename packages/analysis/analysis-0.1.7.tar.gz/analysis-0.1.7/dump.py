#!/usr/bin/env python

"""
Dump a program's instructions.

Copyright (C) 2005, 2006 Paul Boddie <paul@boddie.org.uk>

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

import analysis.source
import analysis.output.utils
import sys
import cmdsyntax

syntax = cmdsyntax.Syntax("""
    <filename> (--CC | --HTML) <output-directory-or-filename>
    """)
matches = syntax.get_args(sys.argv[1:])
try:
    args = matches[0]
except IndexError: 
    print "Syntax:"
    print syntax.syntax
    print "  --CC       Generate C programming language code."
    print "  --HTML     Generate HTML summary."
    sys.exit(1)

session = analysis.source.AnalysisSession()
m = session.process_file(args["filename"])

# C programming language generation.

if args.has_key("CC"):
    directory = args["output-directory-or-filename"]
    analysis.output.utils.generate_sources(session, directory, m._module_name)

# HTML summary.

elif args.has_key("HTML"):
    directory = args["output-directory-or-filename"]
    analysis.output.utils.generate_doc(session, directory)

# vim: tabstop=4 expandtab shiftwidth=4
