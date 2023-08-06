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

"""This module defines events that are published by state machine 
instances."""

from boduch.event import Event

class EventStateMachineAddState(Event):
    """This event is published when a new state is added to a state machine
    instance."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineAddTransition(Event):
    """This event is published when a state transition is added to a
    state machine instance."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineRemoveState(Event):
    """This event is published when a state is removed from a state machine
    instance."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineChangeState(Event):
    """This event is published when the current state of the state machine
    instance has changed."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineTransition(Event):
    """This event is published when a state transition is being executed."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineEqual(Event):
    """This event is published when the state machine instance is used as
    an operator in an equality test."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineNotEqual(Event):
    """This event is published when the state machine instance is used as
    an operator in a non-equality test."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)

__all__=['EventStateMachineAddState', 'EventStateMachineAddTransition',\
         'EventStateMachineRemoveState', 'EventStateMachineChangeState',\
         'EventStateMachineTransition', 'EventStateMachineEqual',\
         'EventStateMachineNotEqual']