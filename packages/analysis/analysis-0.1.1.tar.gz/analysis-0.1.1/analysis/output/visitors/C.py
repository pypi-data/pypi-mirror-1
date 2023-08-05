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

    # Magic function and type numbers.
    # NOTE: Start from a magic place way beyond the built-in type numbers.

    magic_number = 100

    def __init__(self, generator):
        Visitor.__init__(self)

        # Generators.

        self.top_level_generator = RawGenerator(StringIO())
        self.main_generator = RawGenerator(StringIO())
        self.main_generator.indent()
        self.top_level_function_generator = RawGenerator(StringIO())
        self.function_generators = []
        self.generator = generator
        self.in_function = 0
        self.in_module = 0

        # Constant table.

        self.constants = []
        self.constant_values = {}

    def _ltype(self, node):
        names = [cls._qualified_name for cls in ltype(node)]
        if len(names) == 0 and len(lobj(node)) != 0:
            return ["function"]
        else:
            return names

    def _translate(self, name):
        if name in ("int", "float", "long"):
            return "_" + name
        else:
            return name.replace(".", "___")

    def get_generator(self):
        if self.in_module:
            return self.top_level_generator
        elif self.in_function:
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
            for name, nodes in locals:
                if prefix is not None:
                    name = self._translate("%s.%s" % (prefix, name))

                # Specially generate magic values for function and class
                # identifiers.
                # NOTE: This doesn't work with nodes which could be mixtures of
                # NOTE: functions, classes and instances.

                if reduce(lambda result, node: result or isinstance(node, compiler.ast.Function), nodes, 0):
                    self.get_generator().writeln("object_method _%s = {type_method, (reference *) %d, None};" %
                        (self._translate(name), CVisitor.magic_number))
                    self.get_generator().writeln("reference *%s = (reference *) &_%s;" % (self._translate(name), self._translate(name)))
                    CVisitor.magic_number += 1

                elif reduce(lambda result, node: result or isinstance(node, compiler.ast.Class), nodes, 0):
                    self.get_generator().writeln("reference *%s = (reference *) %d;" % (self._translate(name), CVisitor.magic_number))
                    CVisitor.magic_number += 1

                # Do not write out native class attributes.

                elif not self.is_native(node):
                    self.get_generator().writeln("reference *%s;" % name)

            self.get_generator().writeln()

    def write_name(self, node):
        if node._scope == "locals" and node._name_context == "class":
            self.get_generator().write(self._translate(node._qualified_name))
        else:
            self.get_generator().write(self._translate(node.name))

    def write_attr(self, node, obj, attr, attrname, write_case=0):

        """
        For the given 'node' expressing an attribute lookup, Write a reference
        to the attribute of the given object or class 'obj' using the suggested
        'attr' and having the given 'attrname'.
        """

        if isinstance(obj, compiler.ast.Class):
            if write_case:
                self.get_generator().write("(_tmp ==", self._translate(obj._qualified_name), ")?")
            self.get_generator().write("%s___%s" % (self._translate(obj._qualified_name), attrname))
        elif isinstance(obj, analysis.reference.Reference):
            if write_case:
                self.get_generator().write("(TYPEOF(_tmp) == type_%s)?" % self._translate(obj._class._qualified_name))

            # Only create new method references when the method is first
            # extracted through a lookup on the class.

            if hasattr(node, "_name_context") and node._name_context == "class" and isinstance(attr, compiler.ast.Function):
                self.get_generator().write("NEW_METHOD(")
                self.write_name(attr)
                self.get_generator().write(", _tmp)")
            else:
                self.get_generator().write("((object_%s *) _tmp)->%s" % (self._translate(obj._class._qualified_name), attrname))

    def write_new(self, node):

        """
        Write a reference to a new object instantiated by the given 'node'.
        """

        classes = node._instantiates

        if len(classes) > 1:

            for cls in classes:
                self.get_generator().write("(TYPEOF(_tmp) == type_%s)?" % self._translate(cls._qualified_name))

                # Provide the name and the number of attributes.

                size = len(analysis.classes.get_instance_layout(cls))
                self.get_generator().write("NEW_OBJECT(%s) :" % self._translate(cls._qualified_name))

            self.get_generator().write("None")

        elif len(classes) == 1:
            cls = classes[0]
            size = len(analysis.classes.get_instance_layout(cls))
            self.get_generator().write("NEW_OBJECT(%s)" % self._translate(cls._qualified_name))

    def call_function(self, node, trailing_expression=None, push_all=0):

        """
        Write function calls, associated with the given 'node'. Sequences of
        calls are generated in the following form:

        (f1(args) || 1) ? (f2(args) || 1) ? (f3(args) || 1) ? expr : expr : expr : expr

        The 'push_all' flag, if set to a true value, causes the value of each
        call to be put on the expression stack; for example:

        (PUSH(f1(args)) || 1) ? (PUSH(f2(args)) || 1) ? (PUSH(f3(args)) || 1) ? None : None : None : None
        """

        sequence = map(None, node._targets, node._args, node._refcontexts)
        sequence_length = len(sequence) 
        multiple = sequence_length > 1 or trailing_expression is not None
        i = 1
        for targets, args, refcontexts in sequence:

            if multiple:
                self.get_generator().write("(")
            if push_all:
                self.get_generator().write("PUSH(")

            if len(targets) == 1:
                target, t_args, refcontext = targets[0], args[0], refcontexts[0]
                self.get_generator().write(self._translate(target._qualified_name))
                self.write_parameters(node, t_args, refcontext)

            elif len(targets) > 1:

                for target, t_args, refcontext in map(None, targets, args, refcontexts):
                    self.get_generator().write("(FNAME(_tmp) == FNAME(%s))?" % target._original.name)
                    self.get_generator().write(self._translate(target._qualified_name))
                    self.write_parameters(node, t_args, refcontext)
                    self.get_generator().write(":")

                self.get_generator().write("None")

            if push_all:
                self.get_generator().write(")")
            if multiple:
                self.get_generator().write("|| 1)?")

            i += 1

        # Write the trailing expressions.

        if multiple:
            i = sequence_length + 1
            first = 1
            while i > 0:
                if not first:
                    self.get_generator().write(":")
                self.get_generator().write(trailing_expression or "None")
                i -= 1
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

            # Normal method calls.

            if refcontext == "context":
                self.get_generator().write("CONTEXT(_tmp)")

            # Initialiser method calls.

            elif refcontext == "new":
                self.write_new(node)

            # Assignment-related method calls.

            elif refcontext == "expr":
                self.get_generator().write("_expr")

            # Assignment-related method calls (see visitAssTuple).

            elif refcontext == "pop":
                self.get_generator().write("POP()")

            # Expression-related method calls (see visitList).

            elif refcontext == "top":
                self.get_generator().write("TOP()")

            # Iterator-related method calls.

            elif refcontext == "iter":
                self.get_generator().write("TOP()")

            # Uncaught instantiations.
            # NOTE: Is this necessary?

            elif hasattr(node, "_instantiates"):
                self.write_new(node)

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

    def write_signature(self, node):
        self.get_generator().write("reference *%s" % self._translate(node._qualified_name))
        arg_defs = []
        for argname in node.argnames:
            arg_defs.append("reference *%s" % argname)
        self.get_generator().write("(%s)" % ", ".join(arg_defs))

    def get_const_value(self, value):
        if isinstance(value, str):
            return '"' + value.replace('"', '\\"') + '"'
        else:
            return str(value)

    # Visitor methods for statements.

    def visitModule(self, node):

        """
        Visit the module 'node', producing the top-level declarations and
        initialisations. The module is constructed from the contents of the
        generators written in the following order:

          * generator (the main one), producing globals and constants
            * top-level, producing class and object definitions, and function
              declarations
            * function, producing function definitions
          * generator, producing the main function
            * main, producing the main function code
        """

        # Certain globals should be declared only once in the built-in
        # declarations.

        if self.is_builtin_module(node):
            self.generator.writeln("#ifndef _BUILTINS_H_")
            self.generator.writeln("#define _BUILTINS_H_")
            self.generator.writeln()
            self.generator.writeln('#include "runtime.h"')
            self.generator.writeln()

        else:
            self.generator.writeln('#include "runtime.h"')
            self.generator.writeln('#include "builtins.h"')
            self.generator.writeln()

        # Specially direct module locals to the top-level generator.

        self.in_module = 1
        self.get_generator().writeln("/* Module", node._module_name or "builtins", "locals. */")
        self.get_generator().writeln()
        self.write_locals(node)
        self.in_module = 0

        self.generator.writeln()

        # Generate the code.

        self.dispatch(node.node)

        # Build a constant table, writing it straight out.

        if not self.is_builtin_module(node):
            self.generator.writeln("/* Module", node._module_name, "constants. */")
            self.generator.writeln()

            i = 0
            for constant in self.constants:
                type_name = self._ltype(constant)[0]
                self.generator.writeln("object_%s _const_%s = {type_%s, %s};" %
                    (type_name, i, type_name, self.get_const_value(constant.value)))
                i += 1

            self.generator.writeln()

        # Include the top-level code: function declarations and typedefs.

        self.generator.writeln(self.top_level_generator.stream.getvalue())

        # Include the function definitions.

        self.generator.writeln(self.top_level_function_generator.stream.getvalue())

        # Generate the main program.

        if not self.is_builtin_module(node):
            self.generator.writeln("int main(int argc, char *argv[])")
            self.generator.writeln("{")
            self.generator.indent()
            self.generator.writeln("SYSINIT;")
            self.generator.dedent()
            self.generator.writeln(self.main_generator.stream.getvalue())
            self.generator.indent()
            self.generator.writeln("return 0;")
            self.generator.dedent()
            self.generator.writeln("}")
        else:
            self.generator.writeln("#endif /* _BUILTINS_H_ */")

    def visitClass(self, node):

        # Change the emission state.

        in_function = self.in_function
        self.in_function = 0

        self.in_module = 1
        self.get_generator().writeln("/* Class", node.name, "attributes. */")
        self.get_generator().writeln()
        self.write_locals(node, prefix=node._qualified_name)
        self.get_generator().writeln()

        # Do not write the attributes out where the class is defined as being
        # native.

        if not self.is_native(node):

            # First define the instance structure, if appropriate.

            if hasattr(node, "_instances"):
                self.get_generator().writeln("/* Object", node.name, "attributes. */")
                self.get_generator().writeln()
                self.get_generator().writeln("typedef struct object_%s" % self._translate(node._qualified_name))
                self.get_generator().writeln("{")
                self.get_generator().indent()
                self.get_generator().writeln("int type;")
                for attr_name in analysis.classes.get_instance_layout(node).keys():
                    self.get_generator().writeln("reference *%s;" % self._translate(attr_name))
                self.get_generator().dedent()
                self.get_generator().writeln("} object_%s;" % self._translate(node._qualified_name))
                self.get_generator().writeln()

                # Define a type number for the structure.

                self.get_generator().writeln("int type_%s = %d;" % (self._translate(node._qualified_name), CVisitor.magic_number))
                CVisitor.magic_number += 1
                self.get_generator().writeln()

        self.in_module = 0

        # Then generate the class attribute definitions.

        self.dispatch(node.code)

        # Restore the emission state.

        self.in_function = in_function

    def visitFunction(self, node):

        if not hasattr(node, "_specialisation"):
            return

        # Do not write the signature or body out where the function is defined
        # as being native.

        if self.is_native(node):
            return

        # Write the signature out as a declaration.

        self.in_module = 1
        self.get_generator().writeln("/* Function", node._original.name, "signature. */")
        self.get_generator().writeln()
        self.write_signature(node)
        self.get_generator().writeln(";")
        self.get_generator().writeln()
        self.in_module = 0

        # Make a new generator for the function.

        self.function_generators.append(RawGenerator(StringIO()))
        in_function = self.in_function
        self.in_function = 1

        # Write the function to the generator.

        self.get_generator().writeln("/* Function", node._original.name, "implementation. */")
        self.get_generator().writeln()
        self.write_signature(node)
        self.get_generator().writeln()
        self.get_generator().writeln("{")
        self.get_generator().indent()
        self.write_locals(node, include_parameters=0)
        self.dispatch(node.code)

        # Add some special code for initialisers.

        if node._original.name == "__init__":
            self.get_generator().writeln("return self;")

        self.get_generator().dedent()
        self.get_generator().writeln("}")
        self.get_generator().writeln()

        # Write the generated function out to the top level.

        self.in_function = in_function
        self.top_level_function_generator.write(self.function_generators[-1].stream.getvalue())
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
        n = len(node.nodes)
        for i in range(0, n):
            expr = node.nodes[i]
            # NOTE: The usage of builtins___str will need to be changed to a
            # NOTE: method call eventually.
            self.get_generator().write("fprintf(_stream, builtins___str(")
            self.dispatch(expr)
            self.get_generator().writeln("));")
            if i < n - 1:
                self.get_generator().writeln('fprintf(_stream, " ");')
        self.get_generator().writeln('fprintf(_stream, "\\n");')

    def visitIf(self, node):
        first = 1
        short_circuited = 0
        for compare, block in node.tests:
            if short_circuited:
                break

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
            if hasattr(compare, "_ignored"):
                self.get_generator().writeln("/* Ignored. */")
            else:
                self.dispatch(block)
            self.get_generator().dedent()
            self.get_generator().writeln("}")

            if hasattr(compare, "_short_circuited"):
                short_circuited = 1

        if node.else_ is not None and not short_circuited:
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
        for name in node.names:
            self.get_generator().write("extern reference *%s;" % name)

    # Visitor methods for expression nodes.

    def visitAssName(self, node):
        if self.uses_call(node):
            self.write_name(node)
            self.get_generator().write("=")
            self.call_function(node)
            self.get_generator().writeln(";")
        else:
            self.write_name(node)
            self.get_generator().writeln("= _expr;")

    def visitAssTuple(self, node):
        if self.uses_call(node):
            self.call_function(node, push_all=1)
            self.get_generator().writeln(";");

        for assign_node in node.nodes:
            self.dispatch(assign_node)

        self.get_generator().writeln("POP();");

    visitAssList = visitAssTuple

    def visitAssAttr(self, node):
        if self.uses_call(node):
            self.call_function(node)

        # Get the expression used as target.

        self.get_generator().write("(_tmp =")
        self.dispatch(node.expr)
        self.get_generator().write(")?")

        # NOTE: write_attr attribute argument not used.
        # NOTE: This is because it only affects the production of method objects
        # NOTE: which aren't valid on the left hand side of an assignment.

        objs = lobj(node.expr)
        if len(objs) == 1:
            obj = objs[0]
            self.write_attr(node, obj, None, node.attrname)
            self.get_generator().write("= _expr")
        else:
            first = 1
            for obj in objs:
                if not first:
                    self.get_generator().write(":")
                self.write_attr(node, obj, None, node.attrname, write_case=1)
                self.get_generator().write("= _expr")
                first = 0

            self.get_generator().write(": None")

        # Terminate the expression.

        self.get_generator().writeln(": None;")

    def visitGetattr(self, node):

        # Get the expression used as target.

        self.get_generator().write("(_tmp =")
        self.dispatch(node.expr)
        self.get_generator().write(")?")

        """
        objs = lobj(node.expr)
        if len(objs) == 1:
            obj = objs[0]
            self.write_attr(node, obj, node._contexts[obj], node.attrname)
        else:
            for obj in objs:
                self.write_attr(node, obj, node._contexts[obj], node.attrname, write_case=1)

            self.get_generator().write("None")
        """

        items = node._contexts.items()
        single_choice = (len(items) == 1 and len(unique(items[0][1])) == 1)
        for obj, attrs in items:
            first = 1
            for attr in unique(attrs):
                if not first:
                    self.get_generator().write(":")
                self.write_attr(node, obj, attr, node.attrname, write_case=not single_choice)
                first = 0

            if not single_choice:
                self.get_generator().write(": None")

        # Terminate the expression.

        self.get_generator().write(": None")

    def visitCallFunc(self, node):

        """
        Translate this...

        expr(x, y, z)

        ...into this:

        (_tmp = expr) ? (TYPEOF(_tmp) == C) ? new(C, 3) : (TYPEOF(_tmp) == D) ? new(D, 4) : None : None

        ...or this:

        (_tmp = expr) ? (FNAME(_tmp) == FNAME(f)) ? f(x, y, z) : (FNAME(_tmp) == FNAME(g)) ? g(x, y, z) : None : None

        ...or this:

        (_tmp = expr) ? (FNAME(_tmp) == FNAME(f)) ? f(x, y, z) : (FNAME(_tmp) == FNAME(g)) ? g(x, y, z) : None : None
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

        self.get_generator().write(": None")

    def visitName(self, node):
        if not hasattr(node, "_scope"):
            # Unreachable.
            pass
        self.write_name(node)

    def visitConst(self, node):
        if self.constant_values.has_key(node.value):
            n = self.constant_values[node.value]
        else:
            n = len(self.constants)
            self.constants.append(node)
            self.constant_values[node.value] = n
        self.get_generator().write("&_const_%s" % n)

    def visitList(self, node):
        if hasattr(node, "_instantiates"):
            self.get_generator().write("PUSH(")
            self.write_new(node)
            self.get_generator().write(")?")
        if not self.uses_call(node):
            self.get_generator().write("POP() : None")
        else:
            self.call_function(node, "POP()")
            self.get_generator().write(": None")

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

    def visitNot(self, node):
        self.get_generator().write("!(")
        self.dispatch(node.expr)
        self.get_generator().write(")")

# vim: tabstop=4 expandtab shiftwidth=4
