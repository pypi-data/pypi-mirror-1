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

class HandleStateTransitionTransition(Handle):
    
    priority=PRIORITY_CRITICAL
    
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        transition_obj=self.get_event_data("transition")
        if transition_obj.predicate:
            transition_obj.machine.change_state(transition_obj.target)

__all__=['HandleStateTransitionTransition']