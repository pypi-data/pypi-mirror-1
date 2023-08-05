#!/usr/bin/env python

"""
An AST visitor emitting simple instructions.

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
from analysis.common import ltype, lobj
import analysis.classes
import analysis.namespace
import analysis.reference
import compiler

class InstructionVisitor(Visitor):

    """
    A simple abstract-instruction-emitting visitor.

    Special label codes:

    C   constant
    L   label
    E   label (at end of block)
    """

    def __init__(self, generator):

        "Initialise the visitor with the given 'generator'."

        Visitor.__init__(self)
        self.label_counter = 0
        self.module = None
        self.namespaces = []
        self.generator = generator

    # Internal methods.

    def write_locals(self, node, prefix, static=0):

        """
        Write the locals for the given block 'node' having the given name
        'prefix'. This generally should not write any code or static space
        allocation since locals occur upon every visit to a block and thus may
        occur several times for any given block on the stack. However, if the
        optional 'static' parameter is given a true value, static definitions
        (for things like modules and classes) will be written.
        """

        locals = analysis.namespace.get_locals_layout(node)
        self.generator.comment("Local variables:")
        for i in range(0, len(locals)):
            if not static:
                self.generator.comment("%s %s" % (i, locals[i]))
            else:
                self.generator.var("%s___%s" % (prefix, i), locals[i])

    def visit_local(self, node, instruction):

        """
        Write the code needed to access the local referenced by the given
        'node', using the specified 'instruction' method or function to actually
        produce the code.
        """

        ns = self.namespaces[-1]
        qname = ns._qualified_name
        instruction(qname, node.name, analysis.namespace.get_locals_layout(ns).index(node.name))

    def visit_global(self, node, instruction):

        """
        Write the code needed to access the global referenced by the given
        'node', using the specified 'instruction' method or function to actually
        produce the code.
        """

        index = analysis.namespace.get_locals_layout(self.module).index(node.name)
        qname = self.module._module_name
        instruction(qname, node.name, index)

    def call_function(self, node):

        """
        Write the code needed to call the function referenced by the given
        'node', using the specified 'targets' to determine which specialisations
        are involved.
        """

        # Call functions or methods where appropriate.

        for targets, args, refcontext in map(None, node._targets, node._args, node._refcontexts):
            self.generator.begin_call()

            if len(targets) > 1:
                self.generator.begin_table()
                self.generator.fname()

                # Test each calculated target in turn.
                # Note that such tests need to be performed because the value of the
                # expression refers to the original function identifier, not to the
                # specialisation that will be called with the supplied arguments.

                for target, t_args in map(None, targets, args):
                    self.generator.case(target._original.name)
                    self.write_parameters(t_args, refcontext)
                    self.generator.call(target._qualified_name)

                self.generator.end_table()

            elif len(targets) == 1:
                target, t_args = targets[0], args[0]
                self.write_parameters(t_args, refcontext)
                self.generator.call(target._qualified_name)

            self.generator.end_call()

    def write_parameters(self, params, refcontext):

        """
        Write the parameters/arguments for a function call using the 'params'
        list of parameters. The 'refcontext' is used to determine how to refer
        to references used in the call.

        NOTE: Support star and dstar args.
        """

        if self.uses_reference(params):
            call_args = params[1:]
            if refcontext == "context":
                self.generator.context()
            elif refcontext == "expr":
                pass
            elif refcontext == "iter":
                pass
        else:
            call_args = params

        for arg in call_args:
            self.dispatch(arg)
            self.generator.parameter()

    def write_attr(self, instruction, obj, attrname, write_case=0):

        """
        Using the given 'instruction', write a reference to the attribute of the
        given object or class 'obj' with the given 'attrname'. If the optional
        'write_case' parameter is set to a true value, generate a case
        instruction linking the 'obj' or the type of 'obj' to the 'instruction'.
        """

        if isinstance(obj, compiler.ast.Class):
            if write_case:
                self.generator.case(obj._qualified_name)
            layout = analysis.classes.get_class_layout(obj)
            try:
                index = layout.keys().index(attrname)
                instruction(attrname, index)
            except ValueError:
                self.generator.comment("instruction was %s" % instruction.__name__)
                self.generator.new_function_ref("%s.%s" % (obj._qualified_name, attrname))
        elif isinstance(obj, analysis.reference.Reference):
            if write_case:
                self.generator.case(obj._class._qualified_name)
            layout = analysis.classes.get_instance_layout(obj._class)
            try:
                index = layout.keys().index(attrname)
                instruction(attrname, index)
            except ValueError:
                self.generator.comment("instruction was %s" % instruction.__name__)
                self.generator.new_function_ref("%s.%s" % (obj._class._qualified_name, attrname))

    # Visitor methods for statements.

    def visitModule(self, node):
        self.generator.begin_module_header(node._module_name)
        for i in range(0, len(node._constants_table)):
            self.generator.const("C%s" % i, node._constants_table[i])
        self.write_locals(node, node._module_name, static=1)
        self.namespaces.append(node)
        self.module = node
        self.generator.end_module_header(node._module_name)

        self.default(node)
        self.namespaces.pop()
        self.generator.end_module(node._module_name)

    def visitClass(self, node):
        self.generator.comment("Class initialisation for %s" % node._qualified_name)
        self.write_locals(node, node._qualified_name, static=1)
        self.namespaces.append(node)

        self.generator.indent()
        self.dispatch(node.code)
        self.generator.dedent()

        self.namespaces.pop()
        self.generator.comment("End class initialisation for %s" % node._qualified_name)

    def visitFunction(self, node):
        if not hasattr(node, "_original"):
            return

        self.generator.begin_function(node._qualified_name)
        self.generator.comment("Signature %s" % node._signature)
        self.write_locals(node, node._qualified_name)
        self.namespaces.append(node)

        self.generator.indent()
        self.default(node)
        self.generator.dedent()

        self.namespaces.pop()
        self.generator.end_function(node._qualified_name)

    def visitIf(self, node):
        self.generator.comment("if")

        first_label = next_label = self.label_counter
        self.label_counter = self.label_counter + 1

        for compare, block in node.tests:
            self.generator.label("L%s" % next_label)

            next_label = self.label_counter
            self.label_counter = self.label_counter + 1

            self.dispatch(compare)

            self.generator.jump(0, "L%s" % next_label)

            self.dispatch(block)

            self.generator.jump(None, "E%s" % first_label)

        self.generator.label("L%s" % next_label)
        if node.else_ is not None:
            self.dispatch(node.else_)
            self.label_counter = self.label_counter + 1

        self.generator.label("E%s" % first_label)

    def visitWhile(self, node):
        self.generator.comment("while")

        first_label = self.label_counter
        self.label_counter = self.label_counter + 1

        self.generator.label("L%s" % first_label)

        self.dispatch(node.test)

        self.generator.jump(0, "E%s" % first_label)

        self.dispatch(node.body)

        self.generator.jump(None, "L%s" % first_label)

        self.generator.label("E%s" % first_label)
        if node.else_ is not None:
            self.dispatch(node.else_)

    def visitReturn(self, node):
        self.default(node)
        self.generator.return_()

    def visitGlobal(self, node):
        pass

    def visitAssign(self, node):
        self.dispatch(node.expr)

        for target in node.nodes:
            self.dispatch(target)

    # Visitor methods for expression nodes.

    def visitName(self, node):
        if not hasattr(node, "_scope"):
            # Unreachable.
            pass
        elif node._scope == "locals":
            self.visit_local(node, self.generator.load_local)
        else:
            self.visit_global(node, self.generator.load_global)

    def visitConst(self, node):
        self.generator.load_const("C%s" % self.module._constants_table.index(node.value))

    def visitList(self, node):
        for element_node in node.nodes:
            self.dispatch(element_node)
        self.generator.list(len(node.nodes))

    def visitAssName(self, node):

        # Some names directly access the assignment expression. Others, part of
        # AssTuple and AssList, use a special accessor call.

        if self.uses_call(node):
            self.call_function(node)

        if not hasattr(node, "_scope"):
            # Unreachable.
            pass
        elif node._scope == "locals":
            self.visit_local(node, self.generator.store_local)
        else:
            self.visit_global(node, self.generator.store_global)

    def visitAssAttr(self, node):
        self.dispatch(node.expr)
        objs = lobj(node.expr)
        if len(objs) == 1:
            obj = objs[0]
            self.write_attr(self.generator.store_attr, obj, node.attrname)
        else:
            self.generator.begin_table()
            self.generator.type_of()
            for obj in objs:
                self.write_attr(self.generator.store_attr, obj, node.attrname, write_case=1)
            self.generator.end_table()

    def visitGetattr(self, node):
        self.dispatch(node.expr)
        objs = lobj(node.expr)
        if len(objs) == 1:
            obj = objs[0]
            self.write_attr(self.generator.load_attr, obj, node.attrname)
        else:
            self.generator.begin_table()
            self.generator.type_of()
            for obj in objs:
                self.write_attr(self.generator.load_attr, obj, node.attrname, write_case=1)
            self.generator.end_table()

    def visitAssTuple(self, node):
        if self.uses_call(node):
            self.call_function(node)

        for target in node.nodes:
            self.dispatch(target)

        self.generator.pop_top()

    def visitAssList(self, node):
        if self.uses_call(node):
            self.call_function(node)

        for target in node.nodes:
            self.dispatch(target)

    def visitCallFunc(self, node):

        # Get the expression used as target.

        self.dispatch(node.node)

        # Instantiate classes where appropriate.

        if hasattr(node, "_instantiates"):
            classes = node._instantiates
            if len(classes) > 1:
                self.generator.begin_table()

                for cls in classes:
                    self.generator.case(cls._qualified_name)

                    # Provide the name and the number of attributes.

                    size = len(analysis.classes.get_instance_layout(cls))
                    self.generator.new(cls._qualified_name, size)

                self.generator.end_table()

            elif len(classes) == 1:
                self.generator.pop_top()
                size = len(analysis.classes.get_instance_layout(classes[0]))
                self.generator.new(classes[0]._qualified_name, size)

        # NOTE: Consider error situations here.

        if self.uses_call(node):
            self.call_function(node)

    def visitAdd(self, node):
        self.call_function(node)

    def visitSub(self, node):
        self.call_function(node)

    def visitSubscript(self, node):
        self.call_function(node)

    def visitCompare(self, node):
        for op in node._ops:
            self.call_function(op)

# vim: tabstop=4 expandtab shiftwidth=4
