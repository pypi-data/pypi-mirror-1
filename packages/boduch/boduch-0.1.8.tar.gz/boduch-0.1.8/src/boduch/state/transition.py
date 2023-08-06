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

"""This module defines the StateTransition class used to change
the current state of a state machine."""

from zope.interface import implements
from boduch.interface import IStateTransition
from boduch.type import Type
from boduch.event import publish, EventStateTransitionTransition

class StateTransition(Type):
    """The StateTransition class.  Used to change the state of a
    given state machine."""
    implements(IStateTransition)
    def __init__(self, machine=None, target=None, predicate=None):
        """Constructor.  Initialize the StateTransition attributes.
        The machine parameter is a StateMachine instance.  The target
        parameter is the new state the machine will be in upon a
        successful transition.  The predicate parameter is a Predicate
        instance that will determine if a change in state will take
        place."""
        Type.__init__(self)
        self.machine=machine
        self.target=target
        self.predicate=predicate
        
    def transition(self):
        """Perform a state machine transition test.  This method
        will publish a EventStateTransitionTransition event."""
        publish(EventStateTransitionTransition, kw={"transition":self})
    
__all__=['StateTransition']