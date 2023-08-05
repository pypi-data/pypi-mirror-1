#!/usr/bin/env python

"""
Produce HTML summaries of each of the tests, comprising a number of files with
each file describing a module used in a particular test program.

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

import analysis.output.utils
import analysis.source
from glob import glob
import os
import sys
import cmdsyntax

if __name__ == "__main__":

    syntax = cmdsyntax.Syntax("""
        [--debug] [<filename> ...]
        """)

    matches = syntax.get_args(sys.argv[1:])
    try:
        args = matches[0]
    except IndexError:
        print "Syntax:"
        print syntax.syntax
        print "  <filename>     A Python filename to be tested specifically."
        sys.exit(1)

    # Either process only the selected files, or process all the tests.

    if args.has_key("filename"):
        filenames = args["filename"]
    else:
        filenames = glob(os.path.join("tests", "*" + os.path.extsep + "py"))
        filenames.sort()

    for filename in filenames:
        print "%s..." % filename

        html_output = filename[:-3] + "-files"

        try:
            session = analysis.source.AnalysisSession()
            session.process_file(filename)
            analysis.output.utils.generate_doc(session, html_output)
        except analysis.source.NoTargetsError, site:
            analysis.output.utils.unwrap(site, session)
            continue
        except:
            print "Exception in translation - possibly intentional."
            if args.has_key("debug"):
                raise
            else:
                continue

# vim: tabstop=4 expandtab shiftwidth=4
