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
from boduch.state import StateTransition
from boduch import PRIORITY_CRITICAL

class HandleStateMachineAddState(Handle):

    priority=PRIORITY_CRITICAL

    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        machine_obj=self.get_event_data("machine")
        state_obj=self.get_event_data("state")
        machine_obj.allowed_states.append(state_obj)
        
class HandleStateMachineAddTransition(Handle):
    
    priority=PRIORITY_CRITICAL

    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        machine_obj=self.get_event_data("machine")
        target_obj=self.get_event_data("target")
        predicate_obj=self.get_event_data("predicate")
        transition_obj=StateTransition(machine=machine_obj,\
                                       target=target_obj,\
                                       predicate=predicate_obj)
        machine_obj.transitions.append(transition_obj)
        
class HandleStateMachineRemoveState(Handle):
    
    priority=PRIORITY_CRITICAL
    
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        machine_obj=self.get_event_data("machine")
        state_obj=self.get_event_data("state")
        index=0
        for _state in machine_obj.allowed_states:
            if state_obj==_state:
                machine_obj.allowed_states.pop(index)
                break
            index+=1 
            
class HandleStateMachineChangeState(Handle):

    priority=PRIORITY_CRITICAL

    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        machine_obj=self.get_event_data("machine")
        state_obj=self.get_event_data("state")
        if state_obj in machine_obj.allowed_states:
            machine_obj.current_state=state_obj
            
class HandleStateMachineTransition(Handle):
    
    priority=PRIORITY_CRITICAL
    
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        machine_obj=self.get_event_data("machine")
        for transition in machine_obj.transitions:
            transition.transition()

__all__=['HandleStateMachineAddState', 'HandleStateMachineAddTransition',\
         'HandleStateMachineRemoveState', 'HandleStateMachineChangeState',\
         'HandleStateMachineTransition']