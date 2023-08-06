# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 by Gustavo Narea <http://gustavonarea.net/>
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>
#
# Booleano is freedomware: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# Booleano is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Booleano. If not, see <http://www.gnu.org/licenses/>.
"""
Exceptions raised by :mod:`booleano`.

"""

__all__ = ["InvalidOperationError", "BadCallError", "BadFunctionError"]


class BooleanoException(Exception):
    """
    Base class for the exceptions.
    
    """
    pass


#{ Operation-related errors


class InvalidOperationError(BooleanoException):
    """
    Exception raised when trying to apply an operation on an operand that
    doesn't support it.
    
    This exception must only be used for static errors in the expressions, not
    runtime errors.
    
    For example: ``"word" > 10``.
    
    """
    pass


class BadCallError(InvalidOperationError):
    """
    Exception raised when a function is called with wrong parameters.
    
    """
    pass


class BadFunctionError(BooleanoException):
    """
    Exception raised when a function is defined incorrectly.
    
    Because it's aimed at developers, its message doesn't have to be
    translatable.
    
    """


#}
