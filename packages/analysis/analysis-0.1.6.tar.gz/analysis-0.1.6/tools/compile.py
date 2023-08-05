#!/usr/bin/env python

import analysis.output.utils
import analysis.source
from glob import glob
import os
import sys

debug = "--debug" in sys.argv

print "Compiling runtime..."
runtime = os.path.join("tools", "C", "runtime.o")
runtime_source = runtime[:-1] + "c"
os.system("gcc -g -o %s -c %s -Itools/C" % (runtime, runtime_source))

# NOTE: The built-in declarations could be written to a directory belonging
# NOTE: only to each file.

builtins_source = os.path.join("tools", "C", "builtins.h")

filenames = glob(os.path.join("tests", "*" + os.path.extsep + "py"))
filenames.sort()

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
    except:
        print "Exception in translation - possibly intentional."
        continue

    c_objects = []
    for c_source in generated:
        c_object_name, extension = os.path.splitext(c_source)
        if extension == os.path.extsep + "c":
            c_object = c_object_name + os.path.extsep + "o"
            cmd = "gcc -g -c -o %s %s -I%s -Itools/C" % (c_object, c_source, c_sources_dir)
            if debug:
                print cmd
            os.system(cmd)
            c_objects.append(c_object)

    cmd = "gcc -g -o %s %s %s -lgc" % (
        c_program,
        " ".join(c_objects),
        runtime
        )
    if debug:
        print cmd
    os.system(cmd)

    if not os.path.exists(c_program):
        print "Compilation failed."
        continue

    c_output = os.popen(c_program).read()
    py_output = os.popen("python %s" % filename).read()

    if c_output == py_output:
        print filename, "succeeded"
    else:
        print filename, "failed"
        print repr(c_output)
        print repr(py_output)

# vim: tabstop=4 expandtab shiftwidth=4
