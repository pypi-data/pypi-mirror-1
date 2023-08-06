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

"""This module defines event handles for Set events."""

from boduch.handle import Handle
from boduch import PRIORITY_CRITICAL

class HandleSetPush(Handle):
    """Handle that actually places the data onto the set in response to the
    EventSetPush event."""
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        """Run the handle.  First we get the set instance and the new object
        from the event.  Next we acquire the event lock and perform the
        push."""
        set_obj=self.get_event_data('set')
        data=self.get_event_data('obj')
        set_obj.data.append(data)
        
class HandleSetSet(Handle):
    """Handle the actually updates the set data at the specified index."""
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        """Run the handle.  Updates the set with the specified data at the
        specified index."""
        set_obj=self.get_event_data('set')
        index=self.get_event_data('index')
        data=self.get_event_data('obj')
        set_obj.data[index]=data
        
class HandleSetSort(Handle):
    """Handle that actually sorts the data in response to the
    EventSetSort event."""
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        """Run the handle.  First we get the set instance from the event.  
        Next we acquire the event lock and perform the
        sort."""
        set_obj=self.get_event_data('set')
        reverse=self.get_event_data('reverse')
        set_obj.data.sort(reverse=reverse)
        
class HandleSetPop(Handle):
    """Handle that actually pops the specified element from the set object
    at the specified index."""
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        """Run the handle.  First we get the set instance from the event.
        Next we remove the specified item from the set and place the item
        in the result attribute of the set."""
        set_obj=self.get_event_data('set')
        index=self.get_event_data('index')
        set_obj.result=set_obj.data.pop(index)
        
class HandleSetGet(Handle):
    """Handle that actually gets the specified element from the set object
    at the specified index."""
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        """Run the handle.  First we get the set instance from the event.
        Next we retrieve the specified item from the set and place the item
        in the result attribute of the set."""
        set_obj=self.get_event_data('set')
        index=self.get_event_data('index')
        set_obj.result=set_obj.data[index]        
        
__all__=['HandleSetPush', 'HandleSetSet', 'HandleSetSort', 'HandleSetPop',\
         'HandleSetGet']