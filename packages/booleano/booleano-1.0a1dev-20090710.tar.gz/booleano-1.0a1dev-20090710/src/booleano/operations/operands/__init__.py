# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.
"""
Booleano operands.

"""


from booleano.operations import OPERATIONS, OperationNode
from booleano.exc import InvalidOperationError, BadOperandError

__all__ = ("String", "Number", "Set", "Variable", "Function",
           "PlaceholderVariable", "PlaceholderFunction")


class _OperandMeta(type):
    """
    Metaclass for the operands.
    
    It checks that all the operands were defined correctly.
    
    """
    
    def __init__(cls, name, bases, ns):
        """
        Check the operations supported unless told otherwise.
        
        If the class defines the ``bypass_operation_check`` attribute and it
        evaluates to ``True``, :meth:`check_operations` won't be run.
        
        """
        type.__init__(cls, name, bases, ns)
        if not ns.get("bypass_operation_check"):
            cls.check_operations(name, bases, ns)
    
    def check_operations(cls, name, bases, ns):
        """
        Check that the operand supports all the relevant methods.
        
        :raises BadOperandError: If there are problems with the operations
            the operand claims to support.
        
        """
        if not cls.operations.issubset(OPERATIONS):
            raise BadOperandError("Operand %s supports invalid operations" %
                                  name)
        if len(cls.operations) == 0:
            raise BadOperandError("Operand %s must support at least one "
                                  "operation" % name)
        if not cls.is_implemented(cls.to_python):
            raise BadOperandError("Operand %s must define the .to_python() "
                                  "method" % name)
        # Checking the operations supported:
        if ("boolean" in cls.operations and 
            not cls.is_implemented(cls.get_logical_value)):
            raise BadOperandError("Operand %s must define the  "
                                  ".get_logical_value() method" % name)
        if "equality" in cls.operations and not cls.is_implemented(cls.equals):
            raise BadOperandError("Operand %s must define the .equals() "
                                  "method because it supports equalities" %
                                  name)
        if ("inequality" in cls.operations and
            not (
                 cls.is_implemented(cls.less_than) and 
                 cls.is_implemented(cls.greater_than))
            ):
            raise BadOperandError("Operand %s must define the .greater_than() "
                                  "and .less_than() methods because it "
                                  "supports inequalities" % name)
        if ("membership" in cls.operations and
            not (
                 cls.is_implemented(cls.contains) and 
                 cls.is_implemented(cls.is_subset))
            ):
            raise BadOperandError("Operand %s must define the .contains() "
                                  "and .is_subset() methods because it "
                                  "supports memberships" % name)
    
    def is_implemented(cls, method):
        """Check that ``method`` is implemented."""
        return getattr(method, "implemented", True)


class Operand(OperationNode):
    """
    Base class for *unbound* operands.
    
    .. attribute:: operations = set()
        The set of operations supported by this operand.
    
    .. attribute:: bypass_operation_check = True
        Whether it should be checked that the operand really supports the
        operations it claims to support.
    
    """
    
    __metaclass__ = _OperandMeta
    
    bypass_operation_check = True
    
    operations = set()
    
    required_helpers = ()
    
    def to_python(self, **helpers):
        """
        Return the value of this operand as a Python value.
        
        """
        raise NotImplementedError
    to_python.implemented = False
    
    def check_operation(self, operation):
        """
        Check that this operand supports ``operation``.
        
        :param operation: The operation this operand must support.
        :type operation: basestring
        :raises InvalidOperationError: If this operand doesn't support
            ``operation``.
        
        """
        if operation in self.operations:
            return
        raise InvalidOperationError('Operand "%s" does not support operation '
                                    '"%s"' % (repr(self), operation))
    
    #{ Unary operations
    
    def get_logical_value(self, **helpers):
        """
        Return the truth value of the operand.
        
        This is a *boolean* operation.
        
        """
        raise NotImplementedError
    get_logical_value.implemented = False
    
    #{ Binary operations
    
    def equals(self, value, **helpers):
        """
        Check if this operand equals ``value``.
        
        This is an *equality* operation.
        
        """
        raise NotImplementedError
    equals.implemented = False
    
    def greater_than(self, value, **helpers):
        """
        Check if this operand is greater than ``value``.
        
        This is an *inequality* operation.
        
        """
        raise NotImplementedError
    greater_than.implemented = False
    
    def less_than(self, value, **helpers):
        """
        Check if this operand is less than ``value``.
        
        This is an *inequality* operation.
        
        """
        raise NotImplementedError
    less_than.implemented = False
    
    def contains(self, value, **helpers):
        """
        Check if this operand contains ``value``.
        
        This is a *membership* operation.
        
        """
        raise NotImplementedError
    contains.implemented = False
    
    def is_subset(self, value, **helpers):
        """
        Check if ``value`` is a subset of this operand.
        
        This is a *membership* operation.
        
        """
        raise NotImplementedError
    is_subset.implemented = False
    
    #}


# Importing the built-in operands so they can be available from this namespace:
from booleano.operations.operands.constants import String, Number, Set
from booleano.operations.operands.classes import Variable, Function
from booleano.operations.operands.placeholders import (PlaceholderVariable,
                                                       PlaceholderFunction)
