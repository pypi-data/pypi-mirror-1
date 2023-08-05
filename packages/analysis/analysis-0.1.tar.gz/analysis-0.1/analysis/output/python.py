#!/usr/bin/env python

"""
A Python module writer.

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
59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

import compiler, marshal, imp, os, stat, struct, time

def write_function(f, filename="tmp.pyc"):
    write_module(compiler.ast.Module(None, compiler.ast.Stmt([f])), filename)

def write_module(module, target_filename, source_filename=None, syntax_check=1):

    """
    Write the given 'module' to a file with the given 'target_filename'.
    The optional 'source_filename' is used to build the generated file's header.
    The optional 'syntax_check' flag (set by default) ensures that the module is
    syntactically correct.
    """

    code = get_module_code(module, source_filename)
    write_module_code(code, target_filename, source_filename)

def write_module_code(code, target_filename, source_filename):

    """
    Write the given 'code' to a file with the given 'target_filename'.
    The optional 'source_filename' is used to build the generated file's header.
    """

    f = open(target_filename, "wb")
    f.write(get_header(source_filename))
    marshal.dump(code, f)
    f.close()

def get_module_code(module, source_filename=None, syntax_check=1):

    """
    Return the code for the given 'module'.
    The optional 'source_filename' is used to build the generated file's header.
    The optional 'syntax_check' flag (set by default) ensures that the module is
    syntactically correct.
    """

    if source_filename is None:
        source_filename = "xxx.py"
    if syntax_check:
        compiler.syntax.check(module)
    compiler.misc.set_filename(source_filename, module)
    generator = compiler.pycodegen.ModuleCodeGenerator(module)
    return generator.getCode()

def get_header(filename=None):

    "Taken from compiler.pycodegen. Prepare the compiled module header."

    MAGIC = imp.get_magic()
    if filename is not None:
        mtime = os.stat(filename)[stat.ST_MTIME]
    else:
        mtime = int(time.time())
    mtime = struct.pack('<i', mtime)
    return MAGIC + mtime

# vim: tabstop=4 expandtab shiftwidth=4
