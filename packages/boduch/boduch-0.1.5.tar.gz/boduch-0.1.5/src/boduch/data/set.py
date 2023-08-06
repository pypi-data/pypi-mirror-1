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

"""This module defines the Set class which is basically a list that
emits events."""

from zope.interface import implements
from boduch.interface import ISet
from boduch.type import Type
from boduch.event import publish, EventSetPush, EventSetPop,\
                         EventSetGet, EventSetSet, EventSetSort
                        
class SetIterator(object):
    def __init__(self, set):
        self.set=set
        self.cnt=0
        
    def __iter__(self):
        return self
    
    def next(self):
        try:
            result=self.set[self.cnt]
            self.cnt+=1
            return result
        except IndexError:
            raise StopIteration
        
class Set(Type):
    """This is the Set class that emits events."""
    implements(ISet)
    def __init__(self):
        """Constructor.  Initialize the Set data."""
        Type.__init__(self)
        self.data=[]
        self.result=False
        
    def __getitem__(self, key):
        """Allows retrieval of the specified key using Python list notation."""
        return self.get(key)
    
    def __setitem__(self, key, value):
        """Allows setting items using Python list notation."""
        self.set(key, value)
        
    def __delitem__(self, key):
        """Allows deleting items using Python list notation."""
        self.pop(key)
        
    def __iter__(self):
        """Allows iterating through Set instances."""
        return SetIterator(self)
        
    def push(self, obj):
        """Push an object on the list.  This operation emits a EventSetPush
        event."""
        publish(EventSetPush, kw={'set':self, 'obj':obj})
        
    def pop(self, index):
        """Pop an object from the list.  This operation emits a EventSetPop
        event."""
        publish(EventSetPop, kw={'set':self, 'index':index}, atomic=True)
        return self.result
        
    def get(self, index):
        """Retrieve an object from the list.  This operation emits a 
        EventSetGet event."""
        publish(EventSetGet, kw={'set':self, 'index':index}, atomic=True)
        return self.result
    
    def set(self, index, obj):
        """Update the set at the specified index with the specified object.
        This operation emits a EventSetSet event."""
        publish(EventSetSet, kw={'set':self, 'index':index, 'obj':obj})
        
    def sort(self, reverse=False):
        publish(EventSetSort, kw={'set':self, 'reverse':reverse})
        
__all__=['Set', 'SetIterator']