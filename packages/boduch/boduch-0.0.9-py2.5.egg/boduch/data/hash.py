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
from boduch.event import publish, EventHashPush, EventHashPop, EventHashGet

class Hash(Type):
    implements(IHash)
    def __init__(self, data={}):
        """Constructor.  Initialize the Hash data."""
        self.data=data
        
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
