#!/usr/bin/env python

"""
Test program.

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

from analysis.common import *
import analysis.utils
import analysis.source
import sys

if __name__ == "__main__":

    debug = ("--debug" in sys.argv)

    if len(sys.argv) < 2:
        m = analysis.utils.prompt(debug=debug)
    else:
        m = analysis.source.process_file(sys.argv[1], debug=debug)

# vim: tabstop=4 expandtab shiftwidth=4
