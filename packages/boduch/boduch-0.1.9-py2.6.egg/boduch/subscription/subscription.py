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
from boduch.interface import ISubscription
from boduch.type import Type

class Subscription(Type):
    implements(ISubscription)
    
    def __init__(self, event, handle):
        Type.__init__(self)
        self.event=event
        self.handle=handle
        
    def subscribe(self, handle):
        self.event.subscribe(handle)
        
    def unsubscribe(self, handle):
        self.event.unsubscribe(handle)
        
__all__=['Subscription']