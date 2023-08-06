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

from zope.interface import implements
from boduch.interface import IStateMachine
from boduch.type import Type
from boduch.event import publish, EventStateMachineAddState,\
                         EventStateMachineAddTransition,\
                         EventStateMachineRemoveState,\
                         EventStateMachineChangeState,\
                         EventStateMachineTransition

class StateMachine(Type):
    implements(IStateMachine)
    def __init__(self, *args, **kw):
        Type.__init__(self, *args, **kw)
        self.allowed_states=[]
        self.transitions=[]
        self.current_state=None
        
    def add_state(self, state):
        publish(EventStateMachineAddState, kw={"machine":self, "state":state})
        
    def add_transition(self, target, predicate):
        publish(EventStateMachineAddTransition,\
                kw={"machine":self, "target":target, "predicate":predicate})
       
    def remove_state(self, state):
        publish(EventStateMachineRemoveState,\
                kw={"machine":self, "state":state})

    def change_state(self, state):
        publish(EventStateMachineChangeState,\
                kw={"machine":self, "state":state})

    def transition(self):
        publish(EventStateMachineTransition, kw={"machine":self})
   
__all__=['StateMachine']
