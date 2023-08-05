#!/usr/bin/env python

import analysis.output.utils
import analysis.source
from glob import glob
import os

filenames = glob(os.path.join("tests", "*" + os.path.extsep + "py"))
filenames.sort()

for filename in filenames:
    print "%s..." % filename

    html_output = filename[:-3] + "-files"

    try:
        session = analysis.source.AnalysisSession()
        session.process_file(filename)
        analysis.output.utils.generate_doc(session, html_output)
    except:
        print "Exception in translation - possibly intentional."
        continue

# vim: tabstop=4 expandtab shiftwidth=4
