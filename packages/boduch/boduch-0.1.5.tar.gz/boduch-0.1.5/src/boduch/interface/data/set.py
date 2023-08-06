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

"""This module defines the ISet interface."""

from zope.interface import Interface, Attribute

class ISet(Interface):
    """The basic interface for set objects."""
    data=Attribute("The set data.")
    result=Attribute("The set result for retrieving operations.")
    
    def __getitem__(self, key):
        """Allows retrieval of the specified key using Python list notation."""
        
    def __setitem__(self, key, value):
        """Allows setting items using Python list notation."""
        
    def __delitem__(self, key):
        """Allows deleting items using Python list notation."""
        
    def __iter__(self):
        """Allows iterating through Set instances."""
        return SetIterator(self)        
   
    def push(self, obj):
        """Push an object onto the set."""
        
    def pop(self, index):
        """Remove the object at the specified index from the set."""
        
    def get(self, index):
        """Return the object at the specified index."""
        
    def set(self, index, obj):
        """Update the specified index with the specified object."""
        
    def sort(self, reverse=False):
        """Sort the set data."""
        
__all__=['ISet']