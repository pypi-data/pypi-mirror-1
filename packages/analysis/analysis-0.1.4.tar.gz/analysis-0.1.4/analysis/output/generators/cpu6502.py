#!/usr/bin/env python

"""
Code generation classes for the 6502 CPU.

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

from analysis.output.generators.common import AbstractGenerator

class CPU6502Generator(AbstractGenerator):

    def __init__(self, *args):
        AbstractGenerator.__init__(self, *args)
        self.internal_label_counter = 0

    def _new_label(self):
        label = "_L%s" % self.internal_label_counter
        self.internal_label_counter += 1
        return label

    def start_of_code(self):
        self.comment("start of code")
        self.indent()

    def end_of_code(self):
        self.dedent()
        self.comment("end of code")

    def begin_module_header(self, name):
        self.jump(None, "code_for_module")
        self.comment("begin module header for %s" % name)

    def end_module_header(self, name):
        self.comment("end module header for %s" % name)
        self.label("code_for_module")
        self.indent()

    def end_module(self, name):
        self._ls(); print >>self.stream, "rts"
        self.dedent()
        self.comment("end of module")

    def label(self, name):
        self._ls(); print >>self.stream, "%s:" % name

    def comment(self, text):
        self._ls(); print >>self.stream, ";", text

    def var(self, label_name, name):
        self.label(label_name)
        self._ls(); print >>self.stream, ".word 0"

    def const(self, label_name, value):
        self.label(label_name)
        if type(value) == type(""):
            self._ls(); print >>self.stream, ".word type_string"
            self._ls(); print >>self.stream, ".word 0 ; no refcount, content follows"
            self._ls(); print >>self.stream, '.text "%s"' % value
        elif type(value) == type(0):
            self._ls(); print >>self.stream, ".word type_int"
            self._ls(); print >>self.stream, ".word 0 ; no refcount, content follows"
            self._ls(); print >>self.stream, '.word %s' % value
        elif type(value) == type(0L):
            self._ls(); print >>self.stream, ".word type_long"
            self._ls(); print >>self.stream, ".word 0 ; no refcount, content follows"
            self._ls(); print >>self.stream, '.word %s' % value
        elif type(value) == type(0.0):
            self._ls(); print >>self.stream, ".word type_float"
            self._ls(); print >>self.stream, ".word 0 ; no refcount, content follows"
            self._ls(); print >>self.stream, '.word %s' % value
        elif type(value) == type(False):
            self._ls(); print >>self.stream, ".word type_boolean"
            self._ls(); print >>self.stream, ".word 0 ; no refcount, content follows"
            self._ls(); print >>self.stream, '.word %s' % value
        elif type(value) == type(None):
            # Part of the global constant definitions.
            pass
        else:
            # NOTE: Other types not yet supported.
            raise NotImplementedError, type(value)

    def begin_call(self):
        self.comment("begin call")
        self._ls(); print >>self.stream, "jsr begin_call"

    def call(self, name):
        self.comment("call %s" % name)
        self._ls(); print >>self.stream, "jsr", name

    def end_call(self):
        self.comment("end call")
        self._ls(); print >>self.stream, "jsr end_call"

    def context(self):
        self.comment("context")
        self._ls(); print >>self.stream, "jsr context"

    def parameter(self):
        self.comment("parameter")

    def begin_function(self, name):
        self.comment("begin function")
        self.label(name)
        self.indent()

    def end_function(self, name):
        self.load_const("None")
        self.return_()
        self.dedent()
        self.comment("end function")

    def return_(self):
        self.comment("return")
        self._ls(); print >>self.stream, "rts"

    def load_const(self, name):
        self.comment("load const %s" % name)
        self._ls(); print >>self.stream, "lda #<%s" % name
        self._ls(); print >>self.stream, "sta tmpL"
        self._ls(); print >>self.stream, "lda #>%s" % name
        self._ls(); print >>self.stream, "sta tmpH"
        self._ls(); print >>self.stream, "jsr load_const"

    def load_local(self, qname, name, index):
        self.comment("load local %s" % index)
        self._ls(); print >>self.stream, "lda #%s" % index
        self._ls(); print >>self.stream, "sta tmpL"
        self._ls(); print >>self.stream, "jsr load_local"

    def load_global(self, qname, name, index):
        self.comment("load global %s" % index)
        self._ls(); print >>self.stream, "lda #<%s___%s" % (qname, index)
        self._ls(); print >>self.stream, "sta tmpL"
        self._ls(); print >>self.stream, "lda #>%s___%s" % (qname, index)
        self._ls(); print >>self.stream, "sta tmpH"
        self._ls(); print >>self.stream, "jsr load_global"

    def load_attr(self, name, index):
        self.comment("load attr %s" % index)
        self._ls(); print >>self.stream, "LOAD %s AT %s" % (name, index)

    def store_local(self, qname, name, index):
        self.comment("store local %s" % index)
        self._ls(); print >>self.stream, "lda #%s" % index
        self._ls(); print >>self.stream, "sta tmpL"
        self._ls(); print >>self.stream, "jsr store_local"

    def store_global(self, qname, name, index):
        self.comment("store global %s" % index)
        self._ls(); print >>self.stream, "lda #<%s___%s" % (qname, index)
        self._ls(); print >>self.stream, "sta tmpL"
        self._ls(); print >>self.stream, "lda #>%s___%s" % (qname, index)
        self._ls(); print >>self.stream, "sta tmpH"
        self._ls(); print >>self.stream, "jsr store_global"

    def store_attr(self, name, index):
        self.comment("store attr %s" % index)
        self._ls(); print >>self.stream, "STORE %s AT %s" % (name, index)

    def pop_top(self):
        self._ls(); print >>self.stream, "jsr dec_opsp"

    def compare(self, op):
        self._ls(); print >>self.stream, "COMPARE", op

    def jump(self, state, label):
        self.comment("jump %r %s" % (state, label))
        if state is not None:
            next = self._new_label()
            if state:
                self._ls(); print >>self.stream, "bne %s" % next
            else:
                self._ls(); print >>self.stream, "beq %s" % next
            self._ls(); print >>self.stream, "jmp %s" % label
            self.label(next)
        else:
            self._ls(); print >>self.stream, "jmp %s" % label

    def new(self, cls, size):
        self.comment("new %s of size %s" % (cls, size))
        self._ls(); print >>self.stream, "lda #<%s" % size
        self._ls(); print >>self.stream, "sta tmpL"
        self._ls(); print >>self.stream, "lda #>%s" % size
        self._ls(); print >>self.stream, "sta tmpH"
        self._ls(); print >>self.stream, "jsr new"

    def begin_table(self):
        self.comment("begin table")
        self.indent()

    def type_of(self):
        self.comment("type of")

    def case(self, value):
        self.comment("case %s" % value)

    def end_table(self):
        self.dedent()
        self.comment("end table")

    def list(self, number):
        self.comment("list of size %s" % number)

# vim: tabstop=4 expandtab shiftwidth=4
