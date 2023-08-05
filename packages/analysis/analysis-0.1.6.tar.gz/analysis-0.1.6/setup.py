#! /usr/bin/env python

from distutils.core import setup

import analysis

setup(
    name         = "analysis",
    description  = "Source code analysis of Python programs",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/analysis.html",
    version      = analysis.__version__,
    packages     = ["analysis", "analysis.output", "analysis.output.visitors",
                    "analysis.output.generators"]
    )
