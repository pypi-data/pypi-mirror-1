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

"""This module defines the Lesser predicate class."""

from boduch.predicate import Predicate
from boduch.event import publish, EventLesser

class Lesser(Predicate):
    """The Lesser predicate.  This will evaluate to true
    if the first operand is less than the second."""
    def __init__(self, lop, rop):
        """Constructor.  Initialize the base Predicate class."""
        Predicate.__init__(self, lop, rop)
        
    def __nonzero__(self):
        """Special method that is invoked during truth tests
        such as if statements."""
        publish(EventLesser, kw={'predicate':self}, atomic=True)
        return self.result
        
__all__=['Lesser']