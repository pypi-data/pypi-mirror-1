#!/usr/bin/env python

"""
Transform the tests to C programs and compile them, comparing them against the
CPython execution of the original Python code.

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
import time
import cmdsyntax

if __name__ == "__main__":

    syntax = cmdsyntax.Syntax("""
        [--debug] [--only] [--profile] [<filename> ...]
        """)

    matches = syntax.get_args(sys.argv[1:])
    try:
        args = matches[0]
    except IndexError:
        print "Syntax:"
        print syntax.syntax
        print "  --only         Avoids testing the programs."
        print "  --profile      Incorporates profiling support into the programs."
        print "  <filename>     A Python filename to be tested specifically."
        sys.exit(1)

    compile_only = args.has_key("only")

    print "Compiling runtime..."
    runtime = os.path.join("tools", "C", "runtime.o")
    runtime_source = runtime[:-1] + "c"
    flags = ["-g"]
    if args.has_key("profile"):
        flags.append("-pg")
    os.system("gcc %s -o %s -c %s -Itools/C" % (" ".join(flags), runtime, runtime_source))

    # NOTE: The built-in declarations could be written to a directory belonging
    # NOTE: only to each file.

    builtins_source = os.path.join("tools", "C", "builtins.h")

    # Either compile only the selected files, or compile all the tests.

    if args.has_key("filename"):
        filenames = args["filename"]
    else:
        filenames = glob(os.path.join("tests", "*" + os.path.extsep + "py"))
        filenames.sort()

    # Process the files.

    for filename in filenames:
        print "%s..." % filename

        c_sources_dir_base = os.path.splitext(filename)[0]
        c_sources_dir = c_sources_dir_base + "-sources"
        c_program_name = os.path.split(c_sources_dir_base)[-1]
        c_program = os.path.join(c_sources_dir, c_program_name)

        try:
            session = analysis.source.AnalysisSession()
            session.process_file(filename)
            generated = analysis.output.utils.generate_sources(session, c_sources_dir, c_program_name)
        except analysis.source.NoTargetsError, site:
            analysis.output.utils.unwrap(site, session)
            continue
        except:
            print "Exception in translation - possibly intentional."
            if args.has_key("debug"):
                raise
            else:
                continue

        c_objects = []
        for c_source in generated:
            c_object_name, extension = os.path.splitext(c_source)
            if extension == os.path.extsep + "c":
                c_object = c_object_name + os.path.extsep + "o"
                cmd = "gcc %s -c -o %s %s -I%s -Itools/C" % (" ".join(flags), c_object, c_source, c_sources_dir)
                if args.has_key("debug"):
                    print cmd
                os.system(cmd)
                c_objects.append(c_object)

        cmd = "gcc %s -o %s %s %s -lgc -lm" % (
            " ".join(flags),
            c_program,
            " ".join(c_objects),
            runtime
            )

        if args.has_key("debug"):
            print cmd
        os.system(cmd)

        if not os.path.exists(c_program):
            print "Compilation failed."
            continue

        if compile_only:
            continue

        print c_program

        t = time.time()
        c_output = os.popen(c_program).read()
        print "Time:", time.time() - t

        dir_name, leafname = os.path.split(filename)
        module_name, ext = os.path.splitext(leafname)

        py_compile = """python -c 'import sys; sys.path.append("%s"); __import__("%s")'""" % (dir_name, module_name)
        #print py_compile
        py_import_output = os.popen(py_compile)
        py_import_output.read()

        new_filename, ext = os.path.splitext(filename)
        new_filename = new_filename + os.path.extsep + "pyc"
        print new_filename

        t = time.time()
        py_output = os.popen("python %s" % new_filename).read()
        print "Time:", time.time() - t

        if c_output == py_output:
            print "SUCCEEDED:", filename
        else:
            print "FAILED:", filename
            print c_output
            print "--------"
            print py_output
            print "--------"

# vim: tabstop=4 expandtab shiftwidth=4
