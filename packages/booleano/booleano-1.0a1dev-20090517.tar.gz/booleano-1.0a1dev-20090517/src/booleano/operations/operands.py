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
Operands.

TODO: Write a metaclass to check that the operand implements the methods
for the operations it's supposed to support.

"""

from booleano.operations import OPERATIONS
from booleano.exc import InvalidOperationError

__all__ = ["Variable", "String", "Number", "Set"]


class Operand(object):
    """
    Base class for operands.
    
    .. attribute:: operations = set()
        The set of operations supported by this operand.
    
    """
    
    operations = set()
    
    required_helpers = ()
    
    def to_python(self, **helpers):
        """
        Return the value of this operand as a Python value.
        
        """
        raise NotImplementedError
    
    #{ Unary operations
    
    def get_logical_value(self, **helpers):
        """
        Return the truth value of the operand.
        
        This is a *boolean* operation.
        
        """
        raise NotImplementedError
    
    #{ Binary operations
    
    def equals(self, value, **helpers):
        """
        Check if this operand equals ``value``.
        
        This is an *equality* operation.
        
        """
        raise NotImplementedError
    
    def greater_than(self, value, **helpers):
        """
        Check if this operand is greater than ``value``.
        
        This is an *inequality* operation.
        
        """
        raise NotImplementedError
    
    def less_than(self, value, **helpers):
        """
        Check if this operand is less than ``value``.
        
        This is an *inequality* operation.
        
        """
        raise NotImplementedError
    
    def contains(self, value, **helpers):
        """
        Check if this operand contains ``value``.
        
        This is a *membership* operation.
        
        """
        raise NotImplementedError
    
    def is_subset(self, value, **helpers):
        """
        Check if ``value`` is a subset of this operand.
        
        This is a *membership* operation.
        
        """
        raise NotImplementedError
    
    #}


class Variable(Operand):
    """
    User-defined variable.
    
    """
    
    default_names = {}
    
    def __init__(self, global_name, **names):
        """
        Create the variable using ``global_name`` as it's default name.
        
        Additional keyword arguments represent the other names this variable
        can take in different languages.
        
        .. note::
            ``global_name`` does *not* have to be an English/ASCII string.
        
        """
        self.global_name = global_name
        self.names = self.default_names.copy()
        self.names.update(names)


#{ Constants


class Constant(Operand):
    """
    Base class for constant operands.
    
    The only operation that is common to all the constants is equality (see
    :meth:`equals`).
    
    Constants don't rely on helpers -- they are constant!
    
    .. warning::
        This class is available as the base for the built-in :class:`String`,
        :class:`Number` and :class:`Set` classes. User-defined constants aren't
        supported; use :class:`Variable` instead.
    
    """
    
    operations = set(['equality'])
    
    def __init__(self, constant_value):
        """
        Initialize this constant as ``constant_value``.
        
        """
        self.constant_value = constant_value
    
    def to_python(self, **helpers):
        """
        Return the value represented by this constant.
        
        """
        return self.constant_value
    
    def equals(self, value, **helpers):
        """
        Check if this constant equals ``value``.
        
        """
        return self.constant_value == value


class String(Constant):
    u"""
    Constant string.
    
    These constants only support equality operations.
    
    .. note:: **Membership operations aren't supported**
    
        Although both sets and strings are item collections, the former is 
        unordered and the later is ordered. If they were supported, there would
        some ambiguities to sort out, because users would expect the following
        operation results::
        
        - ``"ao" ⊂ "hola"`` is false: If strings were also sets, then the 
          resulting operation would be ``{"a", "o"} ⊂ {"h", "o", "l", "a"}``,
          which is true.
        - ``"la" ∈ "hola"`` is true: If strings were also sets, then the 
          resulting operation would be ``{"l", "a"} ∈ {"h", "o", "l", "a"}``, 
          which would be an *invalid operation* because the first operand must 
          be an item, not a set. But if we make an exception and take the first 
          operand as an item, the resulting operation would be 
          ``"la" ∈ {"h", "o", "l", "a"}``, which is not true.
        
        The solution to the problems above would involve some magic which
        contradicts the definition of a set: Take the second operand as an 
        *ordered collection*. But it'd just cause more trouble, because both
        operations would be equivalent!
        
        Also, there would be other issues to take into account (or not), like
        case-sensitivity.
        
        Therefore, if this functionality is needed, developers should create
        function operators to handle it.
    
    """
    
    def __init__(self, string):
        """Turn ``string`` into a string if it isn't a string yet"""
        string = unicode(string)
        super(String, self).__init__(string)
    
    def equals(self, value, **helpers):
        """Turn ``value`` into a string if it isn't a string yet"""
        value = unicode(value)
        return super(String, self).equals(value, **helpers)


class Number(Constant):
    """
    Float and integer constants.
    
    These constants support inequality operations; see :meth:`greater_than`
    and :meth:`less_than`.
    
    Internally, this number is treated like a float, even if it was an
    integer initially.
    
    """
    
    operations = Constant.operations | set(['inequality'])
    
    def __init__(self, number):
        """
        Turn ``number`` into a float before instantiating this constant.
        
        """
        number = float(number)
        super(Number, self).__init__(number)
    
    def equals(self, value, **helpers):
        """
        Check if this numeric constant equals ``value``.
        
        ``value`` will be turned into a float prior to the comparison, to 
        support strings.
        
        :raises InvalidOperationError: If ``value`` can't be turned into a
            float.
        
        """
        try:
            value = float(value)
        except ValueError:
            raise InvalidOperationError('"%s" is not a number' % value)
        
        return super(Number, self).equals(value, **helpers)
    
    def greater_than(self, value, **helpers):
        """
        Check if this numeric constant is greater than ``value``.
        
        ``value`` will be turned into a float prior to the comparison, to
        support strings.
        
        """
        return self.constant_value > float(value)
    
    def less_than(self, value, **helpers):
        """
        Check if this numeric constant is less than ``value``.
        
        ``value`` will be turned into a float prior to the comparison, to
        support strings.
        
        """
        return self.constant_value < float(value)


class Set(Constant):
    """
    Constant sets.
    
    These constants support membership operations; see :meth:`contains` and
    :meth:`is_subset`.
    
    """
    
    operations = Constant.operations | set(["inequality", "membership"])
    
    def __init__(self, *items):
        """
        Check that each item in ``items`` is an operand before setting up this
        set.
        
        :raises InvalidOperationError: If at least one of the ``items`` is not
            an instance of :class:`Operand`.
        
        """
        for item in items:
            if not isinstance(item, Operand):
                raise InvalidOperationError('Item "%s" is not an operand, so '
                                            'it cannot be a member of a set' %
                                            item)
        super(Set, self).__init__(set(items))
    
    def to_python(self, **helpers):
        """
        Return a set made up of the Python representation of the operands
        contained in this set.
        
        """
        items = set(item.to_python(**helpers) for item in self.constant_value)
        return items
    
    def equals(self, value, **helpers):
        """Check if all the items in ``value`` are the same of this set."""
        value = set(value)
        return value == self.to_python(**helpers)
    
    def less_than(self, value, **helpers):
        """
        Check if this set has less items than the number represented in 
        ``value``.
        
        :raises InvalidOperationError: If ``value`` is not an integer.
        
        """
        try:
            value = float(value)
            if not value.is_integer():
                raise ValueError
        except ValueError:
            raise InvalidOperationError('To compare the amount of items in a '
                                        'set, the operand "%s" has to be an '
                                        'integer')
        return len(self.constant_value) < value
    
    def greater_than(self, value, **helpers):
        """
        Check if this set has more items than the number represented in 
        ``value``.
        
        :raises InvalidOperationError: If ``value`` is not an integer.
        
        """
        try:
            value = float(value)
            if not value.is_integer():
                raise ValueError
        except ValueError:
            raise InvalidOperationError('To compare the amount of items in a '
                                        'set, the operand "%s" has to be an '
                                        'integer')
        return len(self.constant_value) > value
    
    def contains(self, value, **helpers):
        """
        Check that this constant set contains the ``value`` item.
        
        """
        for item in self.constant_value:
            try:
                if item.equals(value, **helpers):
                    return True
            except InvalidOperationError:
                continue
        return False
    
    def is_subset(self, value, **helpers):
        """
        Check that the ``value`` set is a subset of this constant set.
        
        """
        for item in value:
            if not self.contains(item, **helpers):
                return False
        return True


#}
