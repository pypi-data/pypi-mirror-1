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

"""This module defines the StateMachine class used to manage various
states an object may go through."""

from zope.interface import implements
from boduch.interface import IStateMachine
from boduch.type import Type
from boduch.event import publish, EventStateMachineAddState,\
                         EventStateMachineAddTransition,\
                         EventStateMachineRemoveState,\
                         EventStateMachineChangeState,\
                         EventStateMachineTransition

class StateMachine(Type):
    """The StateMachine class is used to manage a pool of various states.
    A StateMachine instance may have a current state."""
    implements(IStateMachine)
    def __init__(self, *args, **kw):
        """Constructor.  Initialize the base Type class as well as the
        StateMachine attributes."""
        Type.__init__(self, *args, **kw)
        self.allowed_states=[]
        self.transitions=[]
        self.current_state=None
        
    def add_state(self, state):
        """Add a new state to the states available to this machine.  This
        method will publish a EventStateMachineAddState event."""
        publish(EventStateMachineAddState, kw={"machine":self, "state":state})
        
    def add_transition(self, target, predicate):
        """Add a new transition to the state transitions available to this
        machine.  This method will publish a EventStateMachineAddTransition
        event."""
        publish(EventStateMachineAddTransition,\
                kw={"machine":self, "target":target, "predicate":predicate})
       
    def remove_state(self, state):
        """Remove the specified state from the states available to this
        machine.  This method will publish a EventStateMachineRemoveState
        event."""
        publish(EventStateMachineRemoveState,\
                kw={"machine":self, "state":state})

    def change_state(self, state):
        """Change the current state of this machine to the specified state.
        This method will publish a EventStateMachineChangeState event."""
        publish(EventStateMachineChangeState,\
                kw={"machine":self, "state":state})

    def transition(self):
        """Execute all state transitions available to this machine,
        possibly changing the current state.  This method will publish a
        EventStateMachineTransition event."""
        publish(EventStateMachineTransition, kw={"machine":self})
        
    def __eq__(self, other):
        """Check if the current state of this machine matches the specified
        state."""
        self.transition()
        return self.current_state==other
    
    def __ne__(self, other):
        """Check if the current state of this machine does not match
        the specified state."""
        self.transition()
        return self.current_state!=other
   
__all__=['StateMachine']
