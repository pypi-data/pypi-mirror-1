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

"""This module defines the interface for the StateMachine class."""

from zope.interface import Interface, Attribute

class IStateMachine(Interface):
    """The IStateMachine interface.  This interface is provided by
    the StateMachine class."""
    allowed_states=Attribute("""The allowed states of the state machine.""")
    transitions=Attribute("""The state transitions of the state machine.""")
    current_state=Attribute("""The current state of the state machine.""")
    
    def add_state(self, state):
        """Add a new state to the machine."""
        
    def add_transition(self, target, predicate):
        """Add a new transition to the state machine."""
        
    def remove_state(self, state):
        """Remove the specified state from the machine."""
        
    def change_state(self, state):
        """Change the current machine state."""
        
    def transition(self):
        """Perform a state transition."""
        
    def __eq__(self, other):
        """Overload the == operator.  Return true
        if the current state is in the specified state."""
    
    def __ne__(self, other):
        """Overload the != operator.  Return true
        if the current state is not in the specified state."""
        
__all__=["IStateMachine"]