#!/usr/bin/env python

from analysis.output.generators.common import RawGenerator
from analysis.output.visitors.C import CVisitor
import analysis.output.utils
import analysis.utils
from glob import glob
import compiler
import os
import sys

preserve_programs = "--preserve" in sys.argv

print "Compiling runtime..."
runtime = os.path.join("tools", "C", "runtime.o")
runtime_source = runtime[:-1] + "c"
os.system("gcc -g -o %s -c %s -Itools/C" % (runtime, runtime_source))

# NOTE: The built-in declarations could be written to a directory belonging
# NOTE: only to each file.

builtins_source = os.path.join("tools", "C", "builtins.h")

filenames = glob(os.path.join("tests", "*.py"))
filenames.sort()

for filename in filenames:
    print "%s..." % filename

    c_source = filename[:-2] + "c"
    c_program = filename[:-3]

    try:
        analysis.output.utils.generate_files(analysis.utils.process_file(filename), c_source, builtins_source)
    except:
        print "Exception in translation - possibly intentional."
        continue

    os.system("gcc -g -o %s %s %s -Itools/C -lgc" % (c_program, c_source, runtime))
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

    os.remove(c_source)
    if not preserve_programs:
        os.remove(c_program)

# vim: tabstop=4 expandtab shiftwidth=4
