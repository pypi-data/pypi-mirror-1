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

"""This module defines the basic Event class which serves as the base class
of any subsequent events that may be implemented in this event system."""

import time
from zope.interface import implements
from boduch.interface import IEvent
from boduch.type import Type
from boduch.event import unsubscribe

class Event(Type):
    """This is the basic Event class which implements the IEvent interface.
    All events in this system should derive from this class."""
    implements(IEvent)
    
    def __init__(self, *args, **kw):
        """This is the Event constructor.  We also initialize the Type class
        here."""
        Type.__init__(self, *args, **kw)
        self.time=time.time()
        
    def get_time(self):
        """Return the time this event occured."""
        return self.time
    
    @classmethod
    def unsubscribe(cls, handle):
        unsubscribe(cls, handle)
                
__all__=['Event']