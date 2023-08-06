#boduch - Simple Python tool library.
#   Copyright (C) 2008  Adam Boduch
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module defines the base Predicate class."""

from zope.interface import implements
from boduch.interface import IPredicate
from boduch.type import Type

class Predicate(Type):
    """The base Predicate class inherited by all other predicates."""
    implements(IPredicate)
    def __init__(self, lop, rop):
        """Constructor.  Initialize the Type class and all attributes."""
        Type.__init__(self)
        self.lop=lop
        self.rop=rop
        self.result=False
        
    def invoke_operators(self):
        """This method returns a tuple containing the operators
        used in the predicate evaluation.  If any of the specified
        operators are callable, an attempt is made to use the 
        return value of invoking the operator instead of the
        operator itself."""
        if callable(self.lop):
            lop=self.lop()
        else:
            lop=self.lop
        if callable(self.rop):
            rop=self.rop()
        else:
            rop=self.rop
        return lop, rop
        
    def __nonzero__(self):
        """Special method that is called during truth tests.
        This method isn't implemented and should be overridden
        by subclasses."""
        raise NotImplementedError("Predicate.__nonzero__")
    
__all__=['Predicate']
