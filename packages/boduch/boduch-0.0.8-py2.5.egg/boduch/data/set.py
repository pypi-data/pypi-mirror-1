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
from boduch.event import publish, lock, unlock, EventSetPush, EventSetPop,\
                         EventSetGet, EventSetSort

class Set(Type):
    """This is the Set class that emits events."""
    implements(ISet)
    def __init__(self, data=[]):
        """Constructor.  Initialize the Set data."""
        self.data=data
        
    def push(self, obj):
        """Push an object on the list.  This operation emits a EventSetPush
        event."""
        publish(EventSetPush, kw={'set':self, 'obj':obj})
        
    def pop(self, index):
        """Pop an object from the list.  This operation emits a EventSetPop
        event."""
        publish(EventSetPop, kw={'set':self, 'index':index})
        lock()
        obj=self.data.pop(index)
        unlock()
        return obj
        
    def get(self, index):
        """Retrieve an object from the list.  This operation emits a 
        EventSetGet event."""
        publish(EventSetGet, kw={'set':self, 'index':index})
        lock()
        obj=self.data[index]
        unlock()
        return obj
        
    def sort(self, reverse=False):
        publish(EventSetSort, kw={'set':self, 'reverse':reverse})
        
__all__=['Set']