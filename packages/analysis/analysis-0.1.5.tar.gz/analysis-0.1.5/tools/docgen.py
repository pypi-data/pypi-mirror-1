#!/usr/bin/env python

import analysis.output.utils
import analysis.source
from glob import glob
import os

filenames = glob(os.path.join("tests", "*.py"))
filenames.sort()

for filename in filenames:
    print "%s..." % filename

    html_output = filename[:-2] + "html"

    try:
        analysis.source.reset()
        analysis.output.utils.generate_doc(analysis.source.process_file(filename), html_output)
    except:
        print "Exception in translation - possibly intentional."
        continue

# vim: tabstop=4 expandtab shiftwidth=4
