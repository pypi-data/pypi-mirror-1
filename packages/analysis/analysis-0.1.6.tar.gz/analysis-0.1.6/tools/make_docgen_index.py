#!/usr/bin/env python

"Make a simple index of the summary files."

import os
from glob import glob
import sys

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
