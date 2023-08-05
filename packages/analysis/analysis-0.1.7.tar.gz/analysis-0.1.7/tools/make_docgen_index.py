#!/usr/bin/env python

"""
Make a simple index of the summary files.

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

import os
from glob import glob
import sys

if __name__ == "__main__":

    if len(sys.argv) > 1:
        base = sys.argv[1]
        print "Base directory specified:", base
    else:
        base = None
        print "No base directory specified."
        print "Continuing with all directories relative to the current location."

    filenames = glob(os.path.join("tests", "*-files"))
    filenames.sort()

    out = open("analysis-summaries.html", "wb")
    out.write(
    """<html>
      <head>
        <title>analysis - Summaries for the Test Programs</title>
      </head>
      <body>
        <h1>Summaries for the Test Programs</h1>
        <ul>""")

    for filename in filenames:
        leafname = os.path.split(filename)[-1]
        program = leafname[:-6]
        if base is not None:
            dirname = os.path.join(base, leafname)
        else:
            dirname = leafname

        out.write("""
          <li><a href="%s/%s.html">%s</a></li>""" % (dirname, program, program))

    out.write("""
        </ul>
      </body>
    </html>""")

    out.close()

# vim: tabstop=4 expandtab shiftwidth=4
