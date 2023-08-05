#!/usr/bin/env python

"""
A Python language visitor.

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

from analysis.output.visitors.common import Visitor
from analysis.common import *
import analysis.reference

class PythonVisitor(Visitor):

    "A simple Python-emitting visitor."

    def __init__(self, generator):
        Visitor.__init__(self)
        self.generator = generator

    def _ltype(self, node):
        names = [cls.name for cls in ltype(node)]
        if len(names) == 0 and len(lobj(node)) != 0:
            return "function"
        else:
            return "|".join(names)

    def default(self, node):
        self.generator.writeln("# default:", node.__class__.__name__)
        Visitor.default(self, node)

    # Visitor methods for statements.

    def visitModule(self, node):
        self.generator.writeln("# module:", node._module_name)
        self.default(node)

    def visitClass(self, node):
        self.generator.write("class", node.name)
        base_names = []
        for base in node.bases:
            base_names.append(base.name)
        if base_names:
            self.generator.writeln("(%s):" % ", ".join(base_names))
        else:
            self.generator.writeln(":")
        self.generator.indent()
        self.dispatch(node.code)
        self.generator.dedent()

    def visitFunction(self, node):
        if not hasattr(node, "_original"):
            return
        self.generator.write("def", node.name)
        arg_defs = []
        self.generator.writeln("(%s):" % ", ".join(node.argnames))
        self.generator.indent()
        for argname in node.argnames:
            self.generator.writeln("#", argname, "|".join(node._signature[argname]))
        self.dispatch(node.code)
        self.generator.dedent()

    def visitStmt(self, node):
        for statement_node in node.nodes:
            self.dispatch(statement_node)
            self.generator.writeln()

    def visitIf(self, node):
        first = 1
        for compare, block in node.tests:
            if not first:
                self.generator.write("elif")
            else:
                self.generator.write("if")
                first = 0
            self.dispatch(compare)
            self.generator.writeln(":")
            self.generator.indent()
            self.dispatch(block)
            self.generator.dedent()

        if node.else_ is not None:
            self.generator.writeln("else:")
            self.generator.indent()
            self.dispatch(node.else_)
            self.generator.dedent()

    def visitWhile(self, node):
        self.generator.write("while")
        self.dispatch(node.test)
        self.generator.writeln(":")
        self.generator.indent()
        self.dispatch(node.body)
        self.generator.dedent()
        if node.else_ is not None:
            self.generator.writeln("else:")
            self.generator.indent()
            self.dispatch(node.else_)
            self.generator.dedent()

    def visitAssign(self, node):
        for assign_node in node.nodes:
            self.dispatch(assign_node)
        self.generator.write("=")
        self.dispatch(node.expr)

    def visitReturn(self, node):
        self.generator.write("return")
        self.dispatch(node.value)

    def visitGlobal(self, node):
        self.generator.write("global")
        first = 1
        for name in node.names:
            if not first:
                self.generator.write(",")
            else:
                first = 0
            self.generator.write(name)

    def visitPass(self, node):
        self.generator.writeln("pass")

    def visitDiscard(self, node):
        self.dispatch(node.expr)

    # Visitor methods for expression nodes.

    def visitAssName(self, node):
        self.visitName(node)

    def visitAssTuple(self, node):
        first = 1
        for assign_node in node.nodes:
            if not first:
                self.generator.write(",")
            else:
                first = 0
            self.dispatch(assign_node)

    visitAssList = visitAssTuple

    def visitAssAttr(self, node):
        self.generator.write(self._ltype(node), "(")
        self.dispatch(node.expr)
        self.generator.write(".%s" % node.attrname)
        self.generator.write(")")

    def visitGetattr(self, node):
        self.generator.write(self._ltype(node), "(")
        self.dispatch(node.expr)
        self.generator.write(".%s" % node.attrname)
        self.generator.write(")")

    def visitCallFunc(self, node):
        if self.uses_call(node):
            self.call_function(node)

    def call_function(self, node, expr=None):
        for targets, args in map(None, node._targets, node._args):
            if len(node._targets) == 1:
                target, t_args = targets[0], args[0]
                self.generator.write(target.name)
                if expr is not None:
                    self.generator.write("(")
                    self.dispatch(expr)
                    self.generator.write(")")
                self.write_parameters(t_args)

            else:
                self.generator.write("switch(")

                first = 1
                for target, t_args in map(None, targets, args):
                    if not first:
                        self.generator.write("|")

                    # Write the name and types.

                    self.generator.write(target.name)
                    arg_defs = []
                    for arg in t_args:
                        arg_defs.append(self._ltype(arg))
                    self.generator.write("(%s)" % ", ".join(arg_defs))

                    # Write the expression and args.

                    if expr is not None:
                        self.generator.write("(")
                        self.dispatch(expr)
                        self.generator.write(")")
                    self.write_parameters(t_args)

                    first = 0

                self.generator.write(")")

    def write_parameters(self, args):

        # NOTE: Support star and dstar arguments.

        if self.uses_reference(args):
            call_args = args[1:]
        else:
            call_args = args

        self.generator.write("(")
        first = 1
        for arg in call_args:
            if not first:
                self.generator.write(",")
            self.dispatch(arg)
            first = 0
        self.generator.write(")")

    def visitName(self, node):
        self.generator.write(self._ltype(node), "(")
        self.generator.write(node.name)
        self.generator.write(")")

    def visitConst(self, node):
        self.generator.write(self._ltype(node), "(")
        self.generator.write(repr(node.value))
        self.generator.write(")")

    def visitList(self, node):
        self.generator.write("[")
        first = 1
        for element in node.nodes:
            if not first:
                self.generator.write(",")
            else:
                first = 0
            self.dispatch(element)
        self.generator.write("]")

    def visitAdd(self, node):
        if self.uses_call(node):
            self.call_function(node)

    def visitSub(self, node):
        if self.uses_call(node):
            self.call_function(node)

    def visitCompare(self, node):
        self.dispatch(node.expr)
        for op, expr in node.ops:
            self.generator.write(op)
            self.dispatch(expr)

# vim: tabstop=4 expandtab shiftwidth=4
