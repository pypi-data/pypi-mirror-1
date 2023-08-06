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
from boduch.interface import ISet
from boduch.type import Type
from boduch.event import publish, lock, unlock, EventSetPush, EventSetPop,\
                         EventSetGet, EventSetSort

class Set(Type):
    implements(ISet)
    def __init__(self, data=[]):
        self.data=data
        
    def push(self, obj):
        publish(EventSetPush, kw={'set':self, 'obj':obj})
        lock()
        self.data.append(obj)
        unlock()
        
    def pop(self, index):
        publish(EventSetPop, kw={'set':self, 'index':index})
        lock()
        obj=self.data.pop(index)
        unlock()
        return obj
        
    def get(self, index):
        publish(EventSetGet, kw={'set':self, 'index':index})
        lock()
        obj=self.data[index]
        unlock()
        return obj
        
    def sort(self, reverse=False):
        publish(EventSetSort, kw={'set':self, 'reverse':reverse})
        lock()
        self.data.sort(reverse=reverse)
        unlock()
        
__all__=['Set']