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
        event_obj=self.data['event']
        set_obj=event_obj.data['set']
        data=event_obj.data['obj']
        set_obj.data.append(data)
        
class HandleSetSet(Handle):
    """Handle the actually updates the set data at the specified index."""
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        """Run the handle.  Updates the set with the specified data at the
        specified index."""
        event_obj=self.data['event']
        set_obj=event_obj.data['set']
        index=event_obj.data['index']
        data=event_obj.data['obj']
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
        event_obj=self.data['event']
        set_obj=event_obj.data['set']
        reverse=event_obj.data['reverse']
        set_obj.data.sort(reverse=reverse)
        
__all__=['HandleSetPush', 'HandleSetSet', 'HandleSetSort']