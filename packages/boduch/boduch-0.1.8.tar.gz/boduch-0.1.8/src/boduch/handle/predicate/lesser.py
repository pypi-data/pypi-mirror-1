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

"""This module defines the HandleLesser event handle."""

from boduch.handle import Handle
from boduch import PRIORITY_CRITICAL

class HandleLesser(Handle):
    """The HandleLesser event handle.  This event handle is
    executed for EventLesser events."""
    
    priority=PRIORITY_CRITICAL
    
    def __init__(self, *args, **kw):
        """Constructor.  Initialize the base Handle class and
        set the handle priority."""
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        """Run the event handle.  First, initialize the 
        required data.  Next, initialize the operators,
        invoking them if necessary.  Finally, assign the 
        result of the comparison."""
        predicate_obj=self.get_event_data('predicate')
        lop, rop=predicate_obj.invoke_operators()
        predicate_obj.result=lop<rop
        
__all__=['HandleLesser']