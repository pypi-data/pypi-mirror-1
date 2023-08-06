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

from boduch.event import Event

class EventStateMachineAddState(Event):
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineAddTransition(Event):
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineRemoveState(Event):
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineChangeState(Event):
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineTransition(Event):
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineEqual(Event):
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventStateMachineNotEqual(Event):
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)

__all__=['EventStateMachineAddState', 'EventStateMachineAddTransition',\
         'EventStateMachineRemoveState', 'EventStateMachineChangeState',\
         'EventStateMachineTransition', 'EventStateMachineEqual',\
         'EventStateMachineNotEqual']