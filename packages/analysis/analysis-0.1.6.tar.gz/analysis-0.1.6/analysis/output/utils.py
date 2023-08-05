#!/usr/bin/env python

"""
Utility functions for output.

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

import compiler, os
import analysis.source
from analysis.output.visitors.C import CVisitor, write_main
from analysis.output.visitors.HTML import HTMLVisitor
from analysis.output.generators.common import RawGenerator

def generate(m, streams, visitor):

    """
    Generate output for the module 'm', sending program definitions to the given
    'streams', using the given 'visitor' class.
    """

    generators = [RawGenerator(stream) for stream in streams]
    v = visitor(*generators)
    compiler.walk(m, v, v)

def generate_files(m, filenames, visitor):

    """
    Generate output for the module 'm', sending program definitions to the files
    with the given 'filenames', using the given 'visitor' class.
    """

    streams = [open(filename, "w") for filename in filenames]
    generate(m, streams, visitor)
    for stream in streams:
        stream.close()

def generate_sources(session, directory, main_module_name, program_name="main", builtins_name="builtins"):

    """
    Using the given 'session', generate output, sending program definitions to
    the given 'directory'. The 'main_module_name' indicates which of the Python
    modules shall be invoked directly in the final program, and the optional
    'program_name' can be used to customise the name of the source file
    containing the invocation. The optional 'builtins_name' can be used to
    customise the name of the file containing built-in functions and classes.

    Return a list of generated filenames.
    """

    ensure_dir(directory)
    generated = []

    program_filename = os.path.join(directory, program_name + os.path.extsep + "c")
    program_file = open(program_filename, "w")
    write_main(RawGenerator(program_file), main_module_name)
    program_file.close()
    generated.append(program_filename)

    builtins_filename = os.path.join(directory, builtins_name + os.path.extsep + "c")
    builtins_header_filename = os.path.join(directory, builtins_name + os.path.extsep + "h")
    generate_files(session.builtins, [builtins_filename, builtins_header_filename], CVisitor)
    generated.append(builtins_filename)

    for name, module in session.modules.items():
        filename = os.path.join(directory, name + os.path.extsep + "c")
        header_filename = os.path.join(directory, name + os.path.extsep + "h")
        generate_files(module, [filename, header_filename], CVisitor)
        generated.append(filename)

    return generated

def generate_doc(session, directory):

    """
    Using the given 'session', generate output, sending program definitions to
    the given 'directory'.

    Return a list of generated filenames.
    """

    ensure_dir(directory)
    generated = []
    for name, module in session.modules.items():
        filename = os.path.join(directory, name + os.path.extsep + "html")
        generate_files(module, [filename], HTMLVisitor)
        generated.append(filename)
    return generated

def ensure_dir(directory):

    "Ensure the presence of 'directory' without any contents."

    if os.path.exists(directory):
        if os.path.isdir(directory):
            for name in os.listdir(directory):
                os.unlink(os.path.join(directory, name))
    else:
        os.mkdir(directory)

# vim: tabstop=4 expandtab shiftwidth=4
