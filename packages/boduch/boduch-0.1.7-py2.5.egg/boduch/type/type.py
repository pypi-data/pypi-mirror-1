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

"""This module defines the base type class.  This class defines some
operator-overloading functionality."""

import types
import uuid
from zope.interface import implements
from boduch.interface import IType

class Type(object):
    """The base type class that defines various comparison operators."""
    implements(IType)
    
    def __init__(self, *args, **kw):
        """Constructor.  Initialize the keyword data.  The data attribute
        is used when computing the length of type instances."""
        self.data=kw
        self.uuid=uuid.uuid1()
        
    def __len__(self):
        """Compute the length of this instance.  We iterate through the 
        values in the data attribute.  We then return the total of all
        integers found in the data attribute."""
        length=0
        for i in self.data.values():
            try:
                if type(i) is types.IntType:
                    length+=i
                    continue
                length+=len(i)
            except (TypeError, AttributeError):
                continue
        return length
    
    def __eq__(self, other):
        """Compare the equality of this instance to another.  We return true
        if the length of the two instances match"""
        return len(self)==len(other)
    
    def __lt__(self, other):
        """Return true if this instance is less than the other instance."""
        return len(self)<len(other)
    
    def __gt__(self, other):
        """Return true if this instance is greater than the other instance."""
        return len(self)>len(other)
    
    def __cmp__(self, other):
        """Return -1 if both instances have a priority attribute and this
        one is less than the other; 1 if both instances have a priority
        attribute and this one is greater than the other; 0 in all other
        cases."""
        if hasattr(self, 'priority') and hasattr(other, 'priority'):
            return cmp(self.priority, other.priority)
        return 0
    
__all__=['Type']