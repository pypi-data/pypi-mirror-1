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

"""This module defines the base event Handler."""

from zope.interface import implements
from boduch.interface import IHandle
from boduch.type import Type

class Handle(Type):
    """The base event handler.  When run, print a simple message.  This
    handler is not very useful on its' own and should be sub-classed."""
    implements(IHandle)
    
    def __init__(self, *args, **kw):
        """Constructor.  Initialize the Type class."""
        Type.__init__(self, *args, **kw)
        
    def run(self):
        """The run method that executes the handle.  This should be redefined
        by sub-classes."""
        raise NotImplementedError("Handle.run()")
    
    def get_event(self):
        """Return the Event instance that caused this handle to be
        instantiated."""
        if self.data.has_key('event'):
            return self.data['event']
        
    def get_event_data(self, key):
        """Return event data from the event data dictionary using the
        specified key."""
        event_obj=self.get_event()
        if event_obj.data.has_key(key):
            return event_obj.data[key]
        
__all__=['Handle']