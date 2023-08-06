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

from zope.interface import implements
from boduch.interface import IHash
from boduch.type import Type
from boduch.data import Set, SetIterator
from boduch.event import publish, EventHashPush, EventHashPop, EventHashGet

"""This module defines the Hash data structure."""

class Hash(Type):
    """This class represents a hash data structure.  It is essentially a
    Python dictionary that emits events."""
    implements(IHash)
    def __init__(self):
        """Constructor.  Initialize the Hash data."""
        self.data={}
        
    def __getitem__(self, key):
        """Allow the retrieval of an item using Python dictionary notation."""
        return self.get(key)
    
    def __setitem__(self, key, value):
        """Allow items to be set using Python dictionary notation."""
        self.push((key, value))
        
    def __delitem__(self, key):
        """Allow items to be deleted using Python dictionary notation."""
        self.pop(key)
        
    def __iter__(self):
        set_obj=Set()
        for key in self.data.keys():
            set_obj.push(key)
        return SetIterator(set_obj)
        
    def push(self, pair):
        """Push key-value pair on the dictionary."""
        publish(EventHashPush, kw={'hash':self, 'pair':pair})
        
    def pop(self, key):
        """Pop an object from the dictionary."""
        publish(EventHashPop, kw={'hash':self, 'key':key})
        obj=self.data[key]
        del self.data[key]
        return obj
        
    def get(self, key):
        """Retrieve an object from the dictionary."""
        publish(EventHashGet, kw={'hash':self, 'key':key})
        obj=self.data[key]
        return obj
    
__all__=['Hash']
