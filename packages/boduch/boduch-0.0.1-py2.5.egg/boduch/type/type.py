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

import types
from zope.interface import implements
from boduch.interface import IType

class Type(object):
    implements(IType)
    
    def __init__(self, *args, **kw):
        self.data=kw
        
    def __len__(self):
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
        return len(self)==len(other)
    
    def __lt__(self, other):
        return len(self)<len(other)
    
    def __gt__(self, other):
        return len(self)>len(other)
    
__all__=['Type']