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

"""This module defines the IHash interface."""

from zope.interface import Interface, Attribute

class IHash(Interface):
    """The basic interface for hash objects."""
    data=Attribute("The hash data.")
    result=Attribute("The hash result for retrieving operations.")
    
    def __getitem__(self, key):
        """Allow the retrieval of an item using Python dictionary notation."""
    
    def __setitem__(self, key, value):
        """Allow items to be set using Python dictionary notation."""
        
    def __iter__(self):
        """Allow iterating through Hash keys."""        
            
    def push(self, pair):
        """Push a key-value pair onto the hash."""
        
    def pop(self, key):
        """Remove the object at the specified key from the hash."""
        
    def get(self, key):
        """Return the object at the specified key."""
        
__all__=['IHash']
