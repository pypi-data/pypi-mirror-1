#!/usr/bin/env python

"""
Source code analysis.

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

import compiler
from compiler.visitor import ASTVisitor

from analysis.common import *
from analysis.namespace import NamespaceRegister
import analysis.arguments
import analysis.classes
import analysis.node
import analysis.operators
import analysis.reference
import analysis.specialisation
import sys

class AnalysisVisitor(ASTVisitor):

    # Top-level node processing.

    def __init__(self, builtins=None, module_name=None, debug=0):

        """
        Initialise the visitor with an optional 'builtins' module and an
        optional 'module_name'.
        """

        ASTVisitor.__init__(self)
        self.builtins = builtins
        self.module_name = module_name
        self.debug = debug

        # Special values - to be completed when processing.

        self.false = None
        self.true = None

        # Special tracking of current operations.

        self.current_module = None
        self.current_specialisations = []
        self.current_blockages = []

        # Initialise namespaces.

        self.globals = {}
        if self.builtins is None:
            self.builtins = self.globals
        else:
            # Define the special values.
            # NOTE: If more than one reference per class becomes permitted, this
            # NOTE: workaround will no longer be necessary and it will become possible
            # NOTE: to just get False and True from the built-in definitions.

            self.false = analysis.reference.Reference(self.builtins["boolean"][0])
            self.true = analysis.reference.Reference(self.builtins["boolean"][0])

    # General node processing.

    def default(self, node, handler):

        """
        Handle a 'node' not explicitly handled elsewhere, using the given
        namespace 'handler'.
        """

        if analysis.operators.is_binary_operator(node):
            self.process_binary_operator(node, handler)
        else:
            if self.debug:
                print >>sys.stderr, "default on", node
            self.depth_first(node, handler)

    def depth_first(self, node, handler, right_to_left=0):

        """
        Traverse the children of the given 'node', using the given 'handler'. If the
        optional 'right_to_left' flag is set, traverse the children in reverse
        order.

        See also visitStmt which also traverses child nodes.
        """

        child_nodes = list(node.getChildNodes())
        if right_to_left:
            child_nodes.reverse()
        for child_node in child_nodes:

            # For convenience, add the parent node.

            child_node._parent = node
            self.dispatch(child_node, handler)

    def process_block(self, node, handler):

        """
        Process the 'node' with the given namespace 'handler' for a block of code.
        """

        self.depth_first(node, handler)
        node._namespace = handler.locals

    # Specific node handlers.

    def visitModule(self, module, handler=None):

        """
        Process the given 'module' node with the optional 'builtins' dictionary.
        If 'builtins' is not specified, combine the globals and built-ins in the
        processed module.
        If the optional 'module_name' is specified, names defined in this module
        will be suitably qualified by this information.
        """

        handler = NamespaceRegister(self.globals, self.globals, self.builtins,
            name_qualifier=self.module_name, name_context="module")

        # Add the constants table to the module.

        self.current_module = module
        module._constants_table = []

        # Process the module.

        self.process_block(module, handler)

        # Add the module name to the module.

        module._qualified_name = module._module_name = self.module_name

    def visitAssign(self, assign, handler):

        "Process the given 'assign' node using the given 'handler'."

        self.dispatch(assign.expr, handler)
        analysis.node.link(assign, assign.expr)

        # Store the expression for use by descendant nodes.

        nodes = assign.nodes[:]
        nodes.reverse()
        for node in nodes:
            node._parent = assign
            self.dispatch(node, handler)

    def visitAssAttr(self, assattr, handler):

        "Process the given 'assattr' node using the given 'handler'."

        self.reset_specialisations(assattr)
        if isinstance(assattr._parent, compiler.ast.AssTuple) or \
            isinstance(assattr._parent, compiler.ast.AssList) or \
            isinstance(assattr._parent, compiler.ast.For):

            self.attach_next_iteration(assattr, handler)
        else:
            analysis.node.link(assattr, assattr._parent)

        self.depth_first(assattr, handler)

        # Link the found attributes to this node's contexts.

        for obj in lobj(assattr.expr, strict=1):

            # Link to this node in the attribute entry.

            if not obj._namespace.has_key(assattr.attrname):
                obj._namespace[assattr.attrname] = [assattr]
            else:
                obj._namespace[assattr.attrname].append(assattr)

    def visitAssName(self, assname, handler):

        "Process the given 'assname' node using the given 'handler'."

        self.reset_specialisations(assname)
        if isinstance(assname._parent, compiler.ast.AssTuple) or \
            isinstance(assname._parent, compiler.ast.AssList) or \
            isinstance(assname._parent, compiler.ast.For):

            self.attach_next_iteration(assname, handler)
        else:
            analysis.node.link(assname, assname._parent)

        handler.store(assname)

    def visitAssTuple(self, asstuple, handler):

        "Process the given 'asstuple' node using the given 'handler'."

        self.reset_specialisations(asstuple)
        if isinstance(asstuple._parent, compiler.ast.AssTuple) or \
            isinstance(asstuple._parent, compiler.ast.AssList) or \
            isinstance(asstuple._parent, compiler.ast.For):

            self.attach_next_iteration(asstuple, handler)
            refcontext = "pop-next"
        else:
            analysis.node.link(asstuple, asstuple._parent)
            refcontext = "top-expr"

        # Investigate this node's contexts.
        # These will either be the result of a next method call, or the parent
        # node's contexts.

        self.attach_iteration(asstuple, lobj(asstuple, strict=1), refcontext, handler)

        for node in asstuple.nodes:
            node._parent = asstuple
            self.dispatch(node, handler)

    def visitClass(self, class_, handler):

        "Process the given 'class_' node using the given 'handler'."

        new_handler = NamespaceRegister(
            {}, handler.globals, handler.builtins,
            name_qualifier=handler.get_qualified_name(class_.name),
            name_context="class")

        # Add the class to the globals.

        new_handler.globals[class_.name] = [class_]

        # Process the class.

        self.process_block(class_, new_handler)

        # As a consequence of process_block, the base class name nodes should refer
        # to actual base class definitions.

        bases = class_.bases[:]
        bases.reverse()
        for base in bases:
            for nodes in base._contexts.values():
                for node in nodes:
                    for key, values in node._namespace.items():
                        if not class_._namespace.has_key(key):
                            class_._namespace[key] = values

        # Add the module name to the class.

        class_._qualified_name = handler.get_qualified_name(class_.name)
        handler.store(class_)

    def visitCallFunc(self, callfunc, handler):

        "Process the given 'callfunc' node using the given 'handler'."

        self.depth_first(callfunc, handler)
        self.reset_specialisations(callfunc)
        self.next_specialisations(callfunc)

        # Prepare contexts - normal function calls do not have any object reference
        # associated with them.

        context_items = callfunc.node._contexts.items()

        # Loop over contexts, annotating the node.

        for obj, attributes in context_items:
            for attribute in attributes:

                if isinstance(attribute, compiler.ast.Function):
                    args = self.get_context_args(callfunc, obj)

                    # Make a specialisation with the arguments.

                    self.call_specialisation(callfunc, attribute, args,
                        "context", handler,
                        callfunc.star_args, callfunc.dstar_args)

                elif isinstance(attribute, compiler.ast.Class):

                    # Make a reference to the class.

                    ref = analysis.reference.instantiate_class(attribute, callfunc)
                    analysis.node.link(callfunc, ref)
                    args = self.get_context_args(callfunc, ref)

                    # NOTE: Find any __init__ method.

                    if attribute._namespace.has_key("__init__"):
                        methods = attribute._namespace["__init__"]
                        for method in methods:

                            # Make a specialisation.

                            self.call_specialisation(callfunc, method, args,
                                "new", handler,
                                callfunc.star_args, callfunc.dstar_args)

    def visitCompare(self, compare, handler):

        "Process the given 'compare' node using the given 'handler'."

        # Compare nodes have an expression and then a sequence of comparisons:
        # expr          1
        #   op1 expr1     < x
        #   op2 expr2     < 5
        # This is equivalent to...
        # and
        #   expr op1 expr1
        #   expr1 op2 expr2

        operations = []

        if not hasattr(compare, "_ops"):
            compare._ops = []
            last_expr = compare.expr
            for op, expr in compare.ops:
                compare._ops.append(analysis.operators.Op(last_expr, op, expr))
                last_expr = expr

        first = 1
        for op in compare._ops:
            if first:
                self.dispatch(op.left, handler)
                first = 0
            self.dispatch(op.right, handler)

            # Produce appropriate specialisations.

            self._process_binary_operator(op, op.left, op.right, op.left_method_name, op.right_method_name, handler)

        # Link to the result of any comparison - a boolean value.

        analysis.node.link(compare, analysis.reference.instantiate_class(handler.builtins["boolean"][0], compare))

    def visitConst(self, const, handler):

        "Process the given 'const' node using the given 'handler'."

        # Test type(const.value) against int, float, string, unicode, complex,
        # producing a reference to built-in objects.

        if type(const.value) == type(0):
            definitions = handler.builtins["int"]
        elif type(const.value) == type(0L):
            definitions = handler.builtins["long"]
        elif type(const.value) == type(0.0):
            definitions = handler.builtins["float"]
        elif type(const.value) == type(""):
            definitions = handler.builtins["string"]
        elif type(const.value) == type(u""):
            definitions = handler.builtins["unicode"]
        elif type(const.value) == type(0j):
            definitions = handler.builtins["complex"]
        elif type(const.value) == type(False):
            definitions = handler.builtins["boolean"]
        else:
            raise TypeError, "Constant with value %s not handled." % repr(const.value)

        for definition in definitions:
            ref = self.get_const_ref(const, definition)
            analysis.node.link(const, ref)

    def visitFor(self, for_, handler):

        "Process the given 'for_' node using the given 'handler'."

        self.dispatch(for_.list, handler)

        # Process iteration over the "list" expression.

        self.reset_specialisations(for_)
        self.attach_iteration(for_, lobj(for_.list, strict=1), "top-expr", handler)

        # Process the assignment for each iteration.
 
        for_.assign._parent = for_
        self.dispatch(for_.assign, handler)

        # Process the loop contents.

        self.process_conditional(for_.body, handler, handler.locals)
        if for_.else_ is not None:
            self.process_conditional(for_.else_, handler, handler.locals)

    def visitFunction(self, function, handler):
        function._globals = handler.globals
        handler.store(function)

    def visitGetattr(self, getattr, handler):

        "Process the given 'getattr' node using the given 'handler'."

        self.depth_first(getattr, handler)

        # Use a mechanism which properly distinguishes between class and
        # instance attributes.

        getattr._contexts = {}
        for obj in lobj(getattr.expr, strict=1):
            attributes = obj._namespace.get(getattr.attrname, [])
            if len(attributes) == 0:
                attributes = obj._class._namespace.get(getattr.attrname, [])
                getattr._name_context = "class"
            elif isinstance(obj, compiler.ast.Class):
                getattr._name_context = "class"
            else:
                getattr._name_context = "instance"

            getattr._contexts[obj] = []
            for attribute in attributes:

                # NOTE: Special case handling?

                if hasattr(attribute, "_contexts"):
                    for ref in lobj(attribute, strict=1):
                        getattr._contexts[obj].append(ref)
                elif isinstance(attribute, compiler.ast.Function):
                    getattr._contexts[obj].append(attribute)

    def visitGlobal(self, global_, handler):
        handler.make_global(global_)

    def visitIf(self, if_, handler):

        "Process the given 'if_' node using the given 'handler'."

        blocks = if_.tests[:]
        if if_.else_ is not None:
            blocks.append((None, if_.else_))

        modified_locals = {}
        short_circuited = 0

        for compare, block in blocks:
            if compare is not None:
                self.dispatch(compare, handler)

                # Short-circuit evaluation for compile-time optimisations.

                if lobj(compare, strict=1) == [self.false]:
                    compare._ignored = 1
                    continue
                elif lobj(compare, strict=1) == [self.true]:
                    compare._short_circuited = 1

            # Skip the block if short-circuited.

            if short_circuited:
                break

            self.process_conditional(block, handler, modified_locals)

            if hasattr(compare, "_short_circuited"):
                short_circuited = 1

        # Merge in existing locals where no "else" clause was specified.

        if if_.else_ is None and not short_circuited:
            self.merge_locals(modified_locals, handler)

        # Replace the existing locals.

        handler.locals = modified_locals

    def visitList(self, list, handler):

        "Process the given 'list' node using the given 'handler'."

        self.depth_first(list, handler)

        list_class = handler.builtins["list"][0]
        ref = analysis.reference.instantiate_class(list_class, list)

        append_method = list_class._namespace["append"][0]

        self.reset_specialisations(list)
        for node in list.nodes:
            self.next_specialisations(list)
            method_args = [ref, node]

            # Using top as refcontext to use the recently instantiated list
            # object.

            self.call_specialisation(list, append_method, method_args, "top",
                handler)

        analysis.node.link(list, ref)

    # NOTE: Change this!

    def visitTuple(self, tuple, handler):

        "Process the given 'tuple' node using the given 'handler'."

        self.depth_first(tuple, handler)

        tuple_class = handler.builtins["tuple"][0]
        ref = analysis.reference.instantiate_class(tuple_class, tuple)

        append_method = tuple_class._namespace["append"][0]

        self.reset_specialisations(tuple)
        for node in tuple.nodes:
            self.next_specialisations(tuple)
            method_args = [ref, node]

            # Using top as refcontext to use the recently instantiated tuple
            # object.

            self.call_specialisation(tuple, append_method, method_args, "top",
                handler)

        analysis.node.link(tuple, ref)

    def visitName(self, name, handler):
        handler.load(name)

    def visitNot(self, not_, handler):
        self.dispatch(not_.expr, handler)
        analysis.node.link(not_, analysis.reference.instantiate_class(handler.builtins["boolean"][0], not_))

    def visitReturn(self, return_, handler):

        "Process the given 'return_' node using the given 'handler'."

        self.depth_first(return_, handler)

        analysis.node.link(return_, return_.value)
        handler.return_node(return_)

    def visitStmt(self, stmt, handler):

        "Process the given 'stmt' node using the given 'handler'."

        child_nodes = list(stmt.getChildNodes())
        for child_node in child_nodes:
            try:
                self.dispatch(child_node, handler)
            except analysis.node.BlockedError, (from_node, to_node):
                handler.add_blocked_node(from_node)

                # NOTE: Do this more cleanly.

                self.current_blockages.append(to_node)

                if self.debug:
                    print >>sys.stderr, "Blocked on"
                    print >>sys.stderr, analysis.utils.get_line(from_node),
                    print >>sys.stderr, "for"
                    print >>sys.stderr, analysis.utils.get_line(to_node),

            # For convenience, add the parent node.

            child_node._parent = stmt

    def visitSlice(self, slice, handler):

        "Process the given 'slice' node using the given 'handler'."

        self.depth_first(slice, handler)
        self.reset_specialisations(slice)
        self.next_specialisations(slice)

        for expr_input in lobj(slice.expr, strict=1):
            if expr_input._namespace.has_key("__getslice__"):
                methods = expr_input._namespace["__getslice__"]
            elif expr_input._class._namespace.has_key("__getslice__"):
                methods = expr_input._class._namespace["__getslice__"]
            else:
                methods = []

            # Need the actual expression node as an argument.

            method_args = [expr_input]
            if slice.lower is not None:
                method_args.append(slice.lower)
            else:
                # NOTE: Creating a None node from nowhere.

                none_value = compiler.ast.Name("None")
                handler.load(none_value)
                method_args.append(none_value)

            if slice.upper is not None:
                method_args.append(slice.upper)
            else:
                # NOTE: Creating a None node from nowhere.

                none_value = compiler.ast.Name("None")
                handler.load(none_value)
                method_args.append(none_value)

            for method in methods:
                self.call_specialisation(slice, method, method_args, "expr",
                    handler)

    def visitSubscript(self, subscript, handler):

        "Process the given 'subscript' node using the given 'handler'."

        self.depth_first(subscript, handler)
        self.reset_specialisations(subscript)
        self.next_specialisations(subscript)

        for expr_input in lobj(subscript.expr, strict=1):
            if expr_input._namespace.has_key("__getitem__"):
                methods = expr_input._namespace["__getitem__"]
            elif expr_input._class._namespace.has_key("__getitem__"):
                methods = expr_input._class._namespace["__getitem__"]
            else:
                methods = []

            # Need the actual expression node as an argument.

            method_args = [expr_input] + subscript.subs
            for method in methods:
                self.call_specialisation(subscript, method, method_args, "expr",
                    handler)

    def visitWhile(self, while_, handler):

        "Process the given 'while_' node using the given 'handler'."

        # NOTE: Should loop over the body (and possibly the test which should also
        # NOTE: be affected by the modified namespace). The else clause should be
        # NOTE: affected by the modifications to the namespace.

        signature = analysis.specialisation.make_signature(handler.locals)
        signatures = []

        while signature not in signatures:
            if self.debug:
                print >>sys.stderr, "Trying while based on", signature
            signatures.append(signature)
            self.process_conditional(while_.test, handler, handler.locals)
            self.process_conditional(while_.body, handler, handler.locals)
            signature = analysis.specialisation.make_signature(handler.locals)

        if while_.else_ is not None:
            self.process_conditional(while_.else_, handler, handler.locals)

    # Internal methods.

    def attach_iteration(self, node, objects, refcontext, handler):

        """
        On the given 'node', attach access to the __iter__ method of the given
        'objects', using the 'refcontext' to indicate the meaning of the
        reference, as well as the 'handler'.
        """

        self.next_specialisations(node)
        analysis.node.reset(node)

        for obj in objects:

            # Access an iterator on the expression.
            # ie. iter = expr.__iter__()

            if obj._namespace.has_key("__iter__"):
                methods = obj._namespace["__iter__"]
            elif obj._class._namespace.has_key("__iter__"):
                methods = obj._class._namespace["__iter__"]
            else:
                if self.debug:
                    print >>sys.stderr, "Warning! Object %s does not support __iter__" % obj
                continue

            for method in methods:
                self.call_specialisation(node, method, [obj], refcontext, handler)

    def attach_next_iteration(self, node, handler):

        """
        On the given 'node', attach a call to the next method of an iterator
        found on the parent node, using the given 'handler'.
        """

        self.next_specialisations(node)

        # Find appropriate access methods.

        for iter_obj in lobj(node._parent, strict=1):

            # Access a next method on an iterator.
            # ie. iter.next()

            if iter_obj._namespace.has_key("next"):
                next_methods = iter_obj._namespace["next"]
            elif iter_obj._class._namespace.has_key("next"):
                next_methods = iter_obj._class._namespace["next"]
            else:
                if self.debug:
                    print >>sys.stderr, "Warning! Object %s does not support next" % iter_obj
                continue

            # Attach a specialisation call to the node, indicating the means of
            # accessing the assignment expression.

            for next_method in next_methods:
                self.call_specialisation(node, next_method, [iter_obj], "iter",
                    handler)

    def process_conditional(self, block, handler, modified_locals):

        """
        Process the conditional 'block' using the given 'handler'.
        Store modifications to the namespace in the 'modified_locals' dictionary.
        """

        # Preserve locals by copying the dictionary.

        locals = {}
        locals.update(handler.locals)

        # Make a separate handler for this block.

        new_handler = NamespaceRegister(locals, handler.globals, handler.builtins, handler.name_qualifier,
            name_context=handler.name_context)

        self.dispatch(block, new_handler)

        # Merge locals back into handler here.
        # NOTE: This may not deal with global definitions properly.

        self.merge_locals(modified_locals, new_handler)

        # Capture results from the local handler.

        handler.return_nodes += new_handler.return_nodes

    def merge_locals(self, modified_locals, new_handler):

        """
        Add entries to the given 'modified_locals' dictionary by examining the
        locals found in the 'new_handler'.
        """

        for name, values in new_handler.locals.items():
            if not modified_locals.has_key(name):
                modified_locals[name] = []
            for value in values:
                if value not in modified_locals[name]:
                    modified_locals[name].append(value)

    def process_binary_operator(self, operator, handler):

        "Process the given 'operator' node using the given 'handler'."

        self.depth_first(operator, handler)

        # Get the method names.

        left_method_name, right_method_name = analysis.operators.get_binary_methods(operator)

        self._process_binary_operator(operator, operator.left, operator.right,
            left_method_name, right_method_name, handler)

    def _process_binary_operator(self, node, left, right, left_method_name, right_method_name, handler):

        """
        Process the binary operator 'node', with the given 'left' and 'right'
        hand side arguments, the specified 'left_method_name' and
        'right_method_name', and the given 'handler'.
        """

        self.reset_specialisations(node)
        self.next_specialisations(node)

        # NOTE: This assumes matching specialisations from both nodes.

        left_inputs = lobj(left, strict=1)
        right_inputs = lobj(right, strict=1)

        incapable_left_inputs = []
        for left_input in left_inputs:

            # Left operand supports the operation.

            if left_input._namespace.has_key(left_method_name):
                methods = left_input._namespace[left_method_name]
            elif left_input._class._namespace.has_key(left_method_name):
                methods = left_input._class._namespace[left_method_name]
            else:
                methods = []

            if methods != []:
                for right_input in right_inputs:
                    method_args = [left_input, right_input]

                    # Make a specialisation for the operation method.

                    for method in methods:
                        try:
                            self.call_specialisation(node, method, method_args,
                                "left-right", handler)
                        except UnboundLocalError, exc:
                            if exc.args[0] == "TypeConstraintError":
                                if left_input not in incapable_left_inputs:
                                    incapable_left_inputs.append(left_input)
                            else:
                                raise
            else:
                incapable_left_inputs.append(left_input)

        # Handle cases where the left input does not have the appropriate method.

        if len(incapable_left_inputs) > 0:
            for right_input in right_inputs:

                # Right operand supports the operation.

                if right_input._namespace.has_key(right_method_name):
                    methods = right_input._namespace[right_method_name]
                elif right_input._class._namespace.has_key(right_method_name):
                    methods = right_input._class._namespace[right_method_name]
                else:
                    methods = []

                if methods != []:
                    for left_input in incapable_left_inputs:
                        method_args = [right_input, left_input]

                        # Make a specialisation for the operation method.

                        for method in methods:
                            try:
                                self.call_specialisation(node, method,
                                    method_args, "right-left", handler)
                            except UnboundLocalError, exc:
                                if exc.args[0] == "TypeConstraintError":
                                    raise TypeError, "Operands %s and %s are not compatible for %s and %s respectively." % (
                                        left_input, right_input, left_method_name, right_method_name)
                                else:
                                    raise
                else:
                    raise TypeError, "Operands %s and %s are not compatible for %s and %s respectively." % (
                        incapable_left_inputs, right_input, left_method_name, right_method_name)

    def get_context_args(self, node, obj):

        """
        For the given 'node', add the self argument as defined by 'obj'.
        """

        if obj is not None and isinstance(obj, analysis.reference.Reference):
            args = node.args[:]
            args.insert(0, obj)
        else:
            args = node.args
        return args

    def make_const(self, instantiator, value):

        """
        Make a new constant for use by the 'instantiator', having the given 'value'.
        """

        const = compiler.ast.Const(value, instantiator.lineno)
        return const

    def get_const_ref(self, const, definition):

        """
        Get the reference to a constant using the given 'const' node and the
        'definition' of the constant type as found in the built-in types.
        """

        ref = analysis.reference.instantiate_class(definition, const)

        # Add the constants to the constants table.

        if const.value not in self.current_module._constants_table:
            self.current_module._constants_table.append(const.value)

        return ref

    def reset_specialisations(self, caller):

        """
        For the given 'caller', reset the specialisations associated with that
        node.
        """

        # Remove previously-stored contexts.

        analysis.node.reset(caller)

        # Remember called specialisations.

        caller._targets = []

        # We remember arguments used for each specialisation here.

        caller._args = []

        # We also remember the context of any reference arguments.

        caller._refcontexts = []

    def next_specialisations(self, caller):

        """
        For the given 'caller', add an entry to the sequence of calls so that
        a new set of specialisations may be recorded.
        """

        caller._targets.append([])
        caller._args.append([])
        caller._refcontexts.append([])

    def call_specialisation(self, caller, method, args, refcontext, handler, star_args=None, dstar_args=None):

        """
        On the given 'caller' node, invoke the given 'method' with the given
        'args', using the specified 'refcontext' to define the meaning of any
        references involved and the 'handler' to provide namespace information.
        The optional 'star_args' and 'dstar_args' may be used to provide
        additional argument information.

        Establish the special _targets attribute on 'caller', and link results
        to that node.
        """

        # Add support for isinstance and other compile-time optimisations.

        if method.doc is not None and "SPECIAL" in [line.strip() for line in method.doc.split("\n")]:
            if self.optimise_specialisation(caller, method, args, handler):
                return

        # Prepare the arguments, unify them with the parameters, specialise the
        # given function, and link to the result.

        star_args = star_args or []
        dstar_args = dstar_args or []
        ns = analysis.arguments.unify_arguments(args, star_args, dstar_args, method)
        spec = self.specialise_function(method, ns, handler)
        analysis.node.merge(caller, spec, blocking=1)

        # Then link to the results of each specialisation.

        if spec not in caller._targets[-1]:
            caller._targets[-1].append(spec)
            caller._args[-1].append(args)
            caller._refcontexts[-1].append(refcontext)

    def optimise_specialisation(self, caller, method, args, handler):

        """
        Using the given 'caller' node, 'method' node, 'args' and namespace 'handler'
        determine whether the call can be optimised at compile time, returning a
        true value and linking the 'caller' appropriately to the optimised result
        value if possible; otherwise, a false value is returned.
        """

        if method.name == "isinstance":
            obj, cls_ref_node = args[0:2]

            # Where the object is always an instance of one of the given classes,
            # link directly to a true value. Where the object is never an instance
            # of one of those classes, link directly to a false value. Otherwise,
            # process the specialisation.

            is_subclass = None

            # Get each class...

            for cls in lobj(cls_ref_node, strict=1):

                # Get each object type/class...

                for obj_cls in ltype(obj):
                    obj_cls_is_subclass = analysis.classes.issubclass(obj_cls, cls)

                    # If not a subclass, if this contradicts previous tests then the
                    # status is undecided.

                    if not obj_cls_is_subclass :
                        if is_subclass == 1:
                            is_subclass = None
                            break
                        else:
                            is_subclass = 0

                    # If a subclass, if this contradicts previous tests then the
                    # status is undecided.

                    elif obj_cls_is_subclass:
                        if is_subclass == 0:
                            is_subclass = None
                            break
                        else:
                            is_subclass = 1

            if is_subclass == 1:
                analysis.node.link(caller, self.true)
                caller._optimised_value = 1
                return 1
            elif is_subclass == 0:
                analysis.node.link(caller, self.false)
                caller._optimised_value = 0
                return 1

        # Otherwise, process the specialisation...

        return 0

    # Special AST transformations.

    def specialise_function(self, function, locals, handler, add_to_module=1):

        """
        Process the given 'function' node using the given 'locals' namespace and the
        given 'handler', producing a specialised version of the function and
        returning a node for that specialisation.

        If the optional 'add_to_module' parameter is set to true, add the
        specialisation as a sibling of the original 'function' in the module.
        """

        # Inspect the parameters and identify existing suitable specialisations.

        signature = analysis.specialisation.make_signature(locals)

        if self.debug:
            print >>sys.stderr
            print >>sys.stderr, "--------"
            print >>sys.stderr, "Trying", function.name, signature
            print >>sys.stderr, "During", [spec.name for spec in self.current_specialisations]

        # Either get an existing specialisation or create a new one.

        specialisation = analysis.specialisation.get_specialisation(function, signature)

        # If this specialisation is already being processed (due to recursion),
        # abort the call.

        if specialisation in self.current_specialisations:
            return specialisation
        else:
            self.current_specialisations.append(specialisation)

        # Add the module name to the specialisation.
        # Find a suitable qualified name. This employs fixed names for certain
        # native implementations.

        if specialisation.doc is not None and specialisation.doc.strip().startswith("NAME:"):
            specialisation._qualified_name = specialisation.doc.split(":")[1].split("\n")[0].strip()

        # Loop until the specialisation is no longer blocking.

        try:
            while 1:

                qualified_name = specialisation._qualified_name

                # Prepare a new namespace for the specialisation.

                new_handler = NamespaceRegister(locals, function._globals, handler.builtins,
                    name_qualifier=qualified_name, name_context="function")

                self.process_block(specialisation, new_handler)
                if self.debug:
                    print >>sys.stderr, "*", new_handler.blocked_nodes
                    print >>sys.stderr, "|", new_handler.return_nodes

                # Attach result information to the specialisation.

                if len(new_handler.return_nodes) != 0:
                    for return_node in new_handler.return_nodes:
                        analysis.node.merge(specialisation, return_node)
                else:
                    # NOTE: Use a more general representation for None.

                    analysis.node.merge(specialisation, None)

                if self.debug:
                    if hasattr(specialisation, "_contexts"):
                        print >>sys.stderr, function.name, signature, "->", specialisation._contexts
                    else:
                        print >>sys.stderr, function.name, signature, "-> ?"

                # NOTE: Here we should either decide to run the specialisation again or to
                # NOTE: just assume that enough information was deduced.
                # NOTE: Check against the targets of the blocked nodes (possibly by
                # NOTE: recording the blocking specialisation), propagating blocked nodes to
                # NOTE: callers.

                if specialisation in self.current_blockages:
                    if self.debug:
                        print >>sys.stderr, "Re-run this!"
                    self.current_blockages.remove(specialisation)
                else:
                    break

            # Add the specialisation to the module.

            if add_to_module and not hasattr(specialisation, "_parent"):
                container = function._parent.nodes
                index = container.index(function)
                container.insert(index + 1, specialisation)
                specialisation._parent = function._parent

            # Add the signature.

            specialisation._signature = signature

        finally:

            # Remove the specialisation from the list of those being processed.

            self.current_specialisations = self.current_specialisations[:-1]

        return specialisation

# vim: tabstop=4 expandtab shiftwidth=4
