#!/usr/bin/env python

"""
A C language visitor.

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
from analysis.output.generators.common import RawGenerator
from analysis.common import *
import analysis.classes
import analysis.namespace
import compiler
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class CVisitor(Visitor):

    "A simple C-emitting visitor."

    def __init__(self, generator):
        Visitor.__init__(self)

        # Generators.

        self.top_level_generator = RawGenerator(StringIO())
        self.main_generator = RawGenerator(StringIO())
        self.main_generator.indent()
        self.function_generators = []
        self.generator = generator
        self.in_function = 0

        # Constant table.

        self.constants = []
        self.constant_values = {}

    def _ltype(self, node):
        names = [cls._qualified_name for cls in ltype(node)]
        if len(names) == 0 and len(lobj(node)) != 0:
            return ["function"]
        else:
            return names

    def _lobj(self, node):
        names = []
        for obj in lobj(node):
            if isinstance(obj, analysis.reference.Reference):
                names.append(obj._class._qualified_name)
            else:
                names.append(obj._qualified_name)
        return names

    def _translate(self, name):
        return name.replace(".", "___")

    def get_generator(self):
        if self.in_function:
            return self.function_generators[-1]
        else:
            return self.main_generator

    def default(self, node):
        self.get_generator().writeln("/* default", node.__class__.__name__, "*/")
        Visitor.default(self, node)

    # Internal methods.

    def write_locals(self, node, prefix=None, include_parameters=1):

        """
        Write the locals for the given block 'node'.
        """

        locals = analysis.namespace.get_locals_layout(node, include_parameters)
        if locals:
            for local in locals:
                if prefix is None:
                    name = local
                else:
                    name = self._translate("%s.%s" % (prefix, local))
                self.get_generator().writeln("void *%s;" % name)
            self.get_generator().writeln()

    def write_attr(self, obj, attrname, write_case=0):

        """
        Write a reference to the attribute of the given object or class 'obj'
        with the given 'attrname'.
        """

        if isinstance(obj, compiler.ast.Class):
            if write_case:
                self.get_generator().write("(_tmp ==", self._translate(obj._qualified_name), ")?")
            self.get_generator().write("%s___%s" % (self._translate(obj._qualified_name), attrname))
        elif isinstance(obj, analysis.reference.Reference):
            if write_case:
                self.get_generator().write("(typeof(_tmp) ==", self._translate(obj._class._qualified_name), ")?")
            self.get_generator().write("((%s) _tmp)->%s" % (self._translate(obj._class._qualified_name), attrname))

    def write_new(self, node):

        """
        Write a reference to a new object instantiated by the given 'node'.
        """

        classes = node._instantiates

        if len(classes) > 1:

            for cls in classes:
                self.get_generator().write("(typeof(_tmp) ==", self._translate(cls._qualified_name), ")?")

                # Provide the name and the number of attributes.

                size = len(analysis.classes.get_instance_layout(cls))
                self.get_generator().write("new(%s) :" % self._translate(cls._qualified_name))

            self.get_generator().write("NULL")

        elif len(classes) == 1:
            cls = classes[0]
            size = len(analysis.classes.get_instance_layout(cls))
            self.get_generator().write("new(%s)" % self._translate(cls._qualified_name))

    def call_function(self, node):

        """
        Write function calls, associated with the given 'node'.
        """

        first = 1
        for targets, args, refcontext in map(None, node._targets, node._args, node._refcontexts):
            if not first:
                self.get_generator().writeln(";")

            if len(targets) == 1:
                target, t_args = targets[0], args[0]
                self.get_generator().write(self._translate(target._qualified_name))
                self.write_parameters(node, t_args, refcontext)

            elif len(targets) > 1:

                for target, t_args in map(None, targets, args):
                    self.get_generator().write("(fname(_tmp) ==", target._original.name, ")?")
                    self.get_generator().write(self._translate(target._qualified_name))
                    self.write_parameters(node, t_args, refcontext)
                    self.get_generator().write(":")

                self.get_generator().write("NULL")

            first = 0

    def write_parameters(self, node, args, refcontext):

        """
        Write the parameters associated with the given function call 'node'
        using the given call 'args' and a 'refcontext' used to indicate how
        reference objects used in the call are to be represented.
        """

        # NOTE: Support star and dstar arguments.

        self.get_generator().write("(")

        if self.uses_reference(args):
            call_args = args[1:]
            if hasattr(node, "_instantiates"):
                self.write_new(node)
            elif refcontext == "context":
                self.get_generator().write("context(_tmp)")
            elif refcontext == "expr":
                self.get_generator().write("_expr")
            elif refcontext == "iter":
                self.get_generator().write("_iter")
            first = 0
        else:
            call_args = args
            first = 1

        for arg in call_args:
            if not first:
                self.get_generator().write(",")
            self.dispatch(arg)
            first = 0

        self.get_generator().write(")")

    def write_compare(self, compare):
        if hasattr(compare, "_optimised_value"):
            self.get_generator().write(str(compare._optimised_value))
        else:
            self.dispatch(compare)

    # Visitor methods for statements.

    def visitModule(self, node):

        self.generator.writeln('#include "runtime.h"')
        self.generator.writeln()

        self.write_locals(node)

        # Generate the code.

        self.dispatch(node.node)

        # Build a constant table, writing it straight out.

        i = 0
        for constant in self.constants:
            type_name = self._ltype(constant)[0]
            self.generator.writeln("object_%s _const_%s = {type_%s, %s};" % (type_name, i, type_name, repr(constant.value)))
            i += 1
        self.generator.writeln()

        # Include the top-level code: function definitions and typedefs.

        self.generator.writeln(self.top_level_generator.stream.getvalue())

        # Generate the main program.

        self.generator.writeln("int main(int argc, char *argv[])")
        self.generator.writeln("{")
        self.generator.writeln(self.main_generator.stream.getvalue())
        self.generator.indent()
        self.generator.writeln("return 0;")
        self.generator.dedent()
        self.generator.writeln("}")

    def visitClass(self, node):

        # Change the emission state.

        in_function = self.in_function
        self.in_function = 0

        self.write_locals(node, prefix=node._qualified_name)

        # First define the instance structure, if appropriate.

        if hasattr(node, "_instances"):
            self.top_level_generator.writeln("typedef struct", self._translate(node._qualified_name))
            self.top_level_generator.writeln("{")
            self.top_level_generator.indent()
            for attr_name in analysis.classes.get_instance_layout(node).keys():
                self.top_level_generator.writeln("void *%s;" % self._translate(attr_name))
            self.top_level_generator.dedent()
            self.top_level_generator.writeln("} %s;" % self._translate(node._qualified_name))
            self.top_level_generator.writeln()

        # Then define the class attributes.

        self.dispatch(node.code)

        # Restore the emission state.

        self.in_function = in_function

    def visitFunction(self, node):

        if not hasattr(node, "_original"):
            return

        # Make a new generator for the function.

        self.function_generators.append(RawGenerator(StringIO()))
        in_function = self.in_function
        self.in_function = 1

        self.write_locals(node, prefix=node._qualified_name, include_parameters=0)

        # Write the function to the generator.

        self.get_generator().write("void *%s" % self._translate(node._qualified_name))
        arg_defs = []
        for argname in node.argnames:
            arg_defs.append("void *%s" % argname)
        self.get_generator().writeln("(%s)" % ", ".join(arg_defs))
        self.get_generator().writeln("{")
        self.get_generator().indent()
        self.dispatch(node.code)
        self.get_generator().dedent()
        self.get_generator().writeln("}")
        self.get_generator().writeln()

        # Write the generated function out to the top level.

        self.in_function = in_function
        self.top_level_generator.write(self.function_generators[-1].stream.getvalue())
        self.function_generators.pop()

    def visitStmt(self, node):
        for statement_node in node.nodes:
            self.dispatch(statement_node)

    def visitDiscard(self, node):
        self.dispatch(node.expr)
        self.get_generator().writeln(";")

    def visitPass(self, node):
        self.get_generator().writeln("/* Pass */")

    def visitPrintnl(self, node):
        self.get_generator().write("_stream =")
        if node.dest is not None:
            self.dispatch(node.dest)
        else:
            self.get_generator().write("stdout")
        self.get_generator().writeln(";")
        for expr in node.nodes:
            self.get_generator().write("fprintf(_stream,")
            self.get_generator().write('"%s", str(')
            self.dispatch(expr)
            self.get_generator().writeln("));")

    def visitIf(self, node):
        first = 1
        for compare, block in node.tests:
            if not first:
                self.get_generator().write("else if")
            else:
                self.get_generator().write("if")
                first = 0

            self.get_generator().write("(")
            self.write_compare(compare)
            self.get_generator().writeln(")")

            self.get_generator().writeln("{")
            self.get_generator().indent()
            self.dispatch(block)
            self.get_generator().dedent()
            self.get_generator().writeln("}")

        if node.else_ is not None:
            self.get_generator().writeln("else")
            self.get_generator().writeln("{")
            self.get_generator().indent()
            self.dispatch(node.else_)
            self.get_generator().dedent()
            self.get_generator().writeln("}")

    def visitWhile(self, node):
        self.get_generator().write("while")

        self.get_generator().write("(")
        self.write_compare(node.test)
        self.get_generator().writeln(")")

        self.get_generator().writeln("{")
        self.get_generator().indent()
        self.dispatch(node.body)
        self.get_generator().dedent()
        self.get_generator().writeln("}")
        if node.else_ is not None:
            self.get_generator().writeln("else")
            self.get_generator().writeln("{")
            self.get_generator().indent()
            self.dispatch(node.else_)
            self.get_generator().dedent()
            self.get_generator().writeln("}")

    def visitAssign(self, node):
        self.get_generator().write("_expr =")
        self.dispatch(node.expr)
        self.get_generator().writeln(";")
        for assign_node in node.nodes:
            self.dispatch(assign_node)

    def visitReturn(self, node):
        self.get_generator().write("return")
        self.dispatch(node.value)
        self.get_generator().writeln(";")

    def visitGlobal(self, node):
        self.get_generator().write("extern")
        first = 1
        for name in node.names:
            if not first:
                self.get_generator().write(",")
            else:
                first = 0
            self.get_generator().write(name)
        self.get_generator().writeln(";")

    # Visitor methods for expression nodes.

    def visitAssName(self, node):
        if self.uses_call(node):
            self.get_generator().write("%s =" % node.name)
            self.call_function(node)
            self.get_generator().writeln(";")
        else:
            self.get_generator().writeln("%s = _expr;" % node.name)

    def visitAssTuple(self, node):
        if self.uses_call(node):
            self.get_generator().write("_iter =")
            self.call_function(node)
            self.get_generator().writeln(";")

        for assign_node in node.nodes:
            self.dispatch(assign_node)

        self.get_generator().writeln("/* NOTE: Old _iter may need restoring here. */")

    visitAssList = visitAssTuple

    def visitAssAttr(self, node):
        if self.uses_call(node):
            self.call_function(node)

        # Get the expression used as target.

        self.get_generator().write("(_tmp =")
        self.dispatch(node.expr)
        self.get_generator().write(")?")

        objs = lobj(node.expr)
        if len(objs) == 1:
            obj = objs[0]
            self.write_attr(obj, node.attrname)
            self.get_generator().write("= _expr")
        else:
            for obj in objs:
                self.write_attr(obj, node.attrname, write_case=1)
                self.get_generator().write("= _expr")

            self.get_generator().write("NULL")

        # Terminate the expression.

        self.get_generator().writeln(": NULL;")

    def visitGetattr(self, node):

        # Get the expression used as target.

        self.get_generator().write("(_tmp =")
        self.dispatch(node.expr)
        self.get_generator().write(")?")

        objs = lobj(node.expr)
        if len(objs) == 1:
            obj = objs[0]
            self.write_attr(obj, node.attrname)
        else:
            for obj in objs:
                self.write_attr(obj, node.attrname, write_case=1)

            self.get_generator().write("NULL")

        # Terminate the expression.

        self.get_generator().write(": NULL")

    def visitCallFunc(self, node):

        """
        Translate this...

        expr(x, y, z)

        ...into this:

        (_tmp = expr) ? (typeof(_tmp) == C) ? new(C, 3) : (typeof(_tmp) == D) ? new(D, 4) : NULL : NULL

        ...or this:

        (_tmp = expr) ? (fname(_tmp) == f) ? f(x, y, z) : (fname(_tmp) == g) ? g(x, y, z) : NULL : NULL

        ...or this:

        (_tmp = expr) ? (fname(_tmp) == f) ? f(x, y, z) : (fname(_tmp) == g) ? g(x, y, z) : NULL : NULL
        """

        # Get the expression used as target.

        self.get_generator().write("(_tmp =")
        self.dispatch(node.node)
        self.get_generator().write(")?")

        if self.uses_call(node):
            self.call_function(node)

        # Instantiate classes where appropriate.

        elif hasattr(node, "_instantiates"):
            self.write_new(node)

        else:
            self.get_generator().write("ERROR")

        # Terminate the expression.

        self.get_generator().write(": NULL")

    def visitName(self, node):
        if not hasattr(node, "_scope"):
            # Unreachable.
            pass
        if hasattr(node, "_qualified_name"):
            self.get_generator().write(node._qualified_name)
        else:
            self.get_generator().write(node.name)

    def visitConst(self, node):
        if self.constant_values.has_key(node.value):
            n = self.constant_values[node.value]
        else:
            n = len(self.constants)
            self.constants.append(node)
            self.constant_values[node.value] = n
        self.get_generator().write("&_const_%s" % n)

    def visitList(self, node):
        self.get_generator().write("[")
        first = 1
        for element in node.nodes:
            if not first:
                self.get_generator().write(",")
            else:
                first = 0
            self.dispatch(element)
        self.get_generator().write("]")

    def visitAdd(self, node):
        if self.uses_call(node):
            self.call_function(node)

    def visitSub(self, node):
        if self.uses_call(node):
            self.call_function(node)

    def visitSubscript(self, node):
        if self.uses_call(node):
            self.call_function(node)

    def visitSlice(self, node):
        if self.uses_call(node):
            self.call_function(node)

    def visitCompare(self, node):
        first = 1
        for op in node._ops:
            if not first:
                self.get_generator().write("&&")
            self.call_function(op)
            first = 0

# vim: tabstop=4 expandtab shiftwidth=4
