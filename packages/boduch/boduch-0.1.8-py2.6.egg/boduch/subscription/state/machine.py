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

from boduch.event import subscribe, EventStateMachineAddState,\
                         EventStateMachineAddTransition,\
                         EventStateMachineRemoveState,\
                         EventStateMachineChangeState,\
                         EventStateMachineTransition
from boduch.handle import HandleStateMachineAddState,\
                          HandleStateMachineAddTransition,\
                          HandleStateMachineRemoveState,\
                          HandleStateMachineChangeState,\
                          HandleStateMachineTransition

SubStateMachineAddState=subscribe(EventStateMachineAddState,\
                                  HandleStateMachineAddState)
SubStateMachineAddTransition=subscribe(EventStateMachineAddTransition,\
                                       HandleStateMachineAddTransition)
SubStateMachineRemoveState=subscribe(EventStateMachineRemoveState,\
                                     HandleStateMachineRemoveState)
SubStateMachineChangeState=subscribe(EventStateMachineChangeState,\
                                     HandleStateMachineChangeState)
SubStateMachineTransition=subscribe(EventStateMachineTransition,\
                                    HandleStateMachineTransition)
                                
__all__=['SubStateMachineAddState', 'SubStateMachineAddTransition',\
         'SubStateMachineRemoveState', 'SubStateMachineChangeState',\
         'SubStateMachineTransition']