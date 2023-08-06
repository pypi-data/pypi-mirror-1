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

from boduch.handle import Handle
from boduch import PRIORITY_CRITICAL

class HandleHashPush(Handle):
    """Handle that actually places the data onto the hash in response to the
    EventHashPush event."""
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        """Run the handle.  First we get the hash instance and the new pair
        from the event.  Next we acquire the event lock and perform the
        push."""
        hash_obj=self.get_event_data('hash')
        pair=self.get_event_data('pair')
        hash_obj.data[pair[0]]=pair[1]
        
class HandleHashPop(Handle):
    """Handle that actually pops the specified item from the hash."""
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        """Run the handle.  First we get the hash instance and the key
        from the event.  Next we place the specified item in the result
        attribute of the hash instance."""
        hash_obj=self.get_event_data('hash')
        key=self.get_event_data('key')
        obj=hash_obj.data[key]
        del hash_obj.data[key]
        hash_obj.result=obj
        
class HandleHashGet(Handle):
    """Handle that actually gets the specified item from the hash."""
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        """Run the handle.  First we get the hash instance from the event.  
        Next we place the retrieved item in the result attribute of the
        hash instance."""
        hash_obj=self.get_event_data('hash')
        key=self.get_event_data('key')
        obj=hash_obj.data[key]
        hash_obj.result=obj
        
__all__=['HandleHashPush', 'HandleHashPop', 'HandleHashGet']