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

"""This module defines the base event handle Subscription class."""

from zope.interface import implements
from boduch.interface import ISubscription
from boduch.type import Type

class Subscription(Type):
    """The Subscription class.  Instances of this class represent a
    specific handle subscribing to a specific event."""
    implements(ISubscription)
    
    def __init__(self, event, handle):
        """Constructor.  Initialize the event class and the handle class."""
        Type.__init__(self)
        self.event=event
        self.handle=handle
        
    def subscribe(self, handle):
        """Subscribe an additional handle to the event represented by this
        subscription instance."""
        return self.event.subscribe(handle)
        
    def unsubscribe(self, handle):
        """Unsubscribe a handle from the event represented by this
        subscription instance."""
        self.event.unsubscribe(handle)
        
__all__=['Subscription']