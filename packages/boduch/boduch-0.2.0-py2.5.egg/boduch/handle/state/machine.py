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

"""This module defines event handles for StateMachine events."""

from boduch.handle import Handle
from boduch.state import StateTransition
from boduch import PRIORITY_CRITICAL

class HandleStateMachineAddState(Handle):
    """Handle for adding states to StateMachine instances.  This
    handle is executed with a PRIORITY_CRITICAL priority."""

    priority=PRIORITY_CRITICAL

    def __init__(self, *args, **kw):
        """Constructor.  Initialize the base Handle class."""
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        """Execute the event handle.  Append the new state to the
        allowed_states attribute of the state machine."""
        machine_obj=self.get_event_data("machine")
        state_obj=self.get_event_data("state")
        machine_obj.allowed_states.append(state_obj)
        
class HandleStateMachineAddTransition(Handle):
    """Handle for adding transitions to StateMachine instances.  This
    handle is executed with a PRIORITY_CRITICAL priority."""
    
    priority=PRIORITY_CRITICAL

    def __init__(self, *args, **kw):
        """Constructor.  Initialize the base Handle class."""
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        """Execute the event handle.  Append the new transition to the
        transitions attribute of the state machine."""
        machine_obj=self.get_event_data("machine")
        target_obj=self.get_event_data("target")
        predicate_obj=self.get_event_data("predicate")
        transition_obj=StateTransition(machine=machine_obj,\
                                       target=target_obj,\
                                       predicate=predicate_obj)
        machine_obj.transitions.append(transition_obj)
        
class HandleStateMachineRemoveState(Handle):
    """Handle for removing states from StateMachine instances.  This
    handle is executed with a PRIORITY_CRITICAL priority."""
    
    priority=PRIORITY_CRITICAL
    
    def __init__(self, *args, **kw):
        """Constructor.  Initialize the base Handle class."""
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        """Execute the event handle.  Iterate through the allowed_states
        until the specified state is found and remove it."""
        machine_obj=self.get_event_data("machine")
        state_obj=self.get_event_data("state")
        index=0
        for _state in machine_obj.allowed_states:
            if state_obj==_state:
                machine_obj.allowed_states.pop(index)
                break
            index+=1 
            
class HandleStateMachineChangeState(Handle):
    """Handle for changing the current state of a StateMachine
    instance.  This handle is executed with a PRIORITY_CRITICAL
    priority."""

    priority=PRIORITY_CRITICAL

    def __init__(self, *args, **kw):
        """Constructor.  Initialize the base Handle class."""
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        """Execute the event handle.  First, ensure that the
        StateMachine is allowed to be in the target state.  If
        so, change the current state."""
        machine_obj=self.get_event_data("machine")
        state_obj=self.get_event_data("state")
        if state_obj in machine_obj.allowed_states:
            machine_obj.current_state=state_obj
            
class HandleStateMachineTransition(Handle):
    """Handle for transitioning StateMachine instances.  This
    handle is executed with a PRIORITY_CRITICAL priority."""
    
    priority=PRIORITY_CRITICAL
    
    def __init__(self, *args, **kw):
        """Constructor.  Initialize the base Handle class."""
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        """Execute the event handle.  Iterate through the
        transitions of the StateMachine instance and
        execute each transition."""
        machine_obj=self.get_event_data("machine")
        for transition in machine_obj.transitions:
            transition.transition()
            
class HandleStateMachineEqual(Handle):
    """Handle for testing the equality of the current state
    of StateMachine instances."""
    
    priority=PRIORITY_CRITICAL
    
    def __init__(self, *args, **kw):
        """Constructor.  Initialize the base Handle class."""
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        """Execute the event handle.  First, transition the
        StateMachine instance.  Then, assign the result of
        the current state comparison to the equal_result attribute."""
        machine_obj=self.get_event_data("machine")
        other=self.get_event_data("other")
        machine_obj.transition()
        machine_obj.equal_result=machine_obj.current_state==other
        
class HandleStateMachineNotEqual(Handle):
    """Handle for testing the non-equality of the current state
    of StateMachine instances."""
    
    priority=PRIORITY_CRITICAL
    
    def __init__(self, *args, **kw):
        """Constructor.  Initialize the base Handle class."""
        Handle.__init__(self, *args, **kw)
        
    def run(self):
        """Execute the event handle.  First, transition the
        StateMachine instance.  Then, assign the result of
        the current state comparison to the not_equal_result attribute."""
        machine_obj=self.get_event_data("machine")
        other=self.get_event_data("other")
        machine_obj.transition()
        machine_obj.not_equal_result=machine_obj.current_state!=other        

__all__=['HandleStateMachineAddState', 'HandleStateMachineAddTransition',\
         'HandleStateMachineRemoveState', 'HandleStateMachineChangeState',\
         'HandleStateMachineTransition', 'HandleStateMachineEqual',\
         'HandleStateMachineNotEqual']