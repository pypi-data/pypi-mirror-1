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

"""This package contains the interface modules used in the boduch Python
library."""

from boduch.interface.event import IEventThread, IEvent, IEventManager,\
                                   IThreadManager
from boduch.interface.type import IType
from boduch.interface.handle import IHandle
from boduch.interface.data import ISet, IHash
from boduch.interface.predicate import IPredicate
from boduch.interface.state import IStateMachine, IStateTransition
from boduch.interface.subscription import ISubscription

__all__=['IEventThread', 'IEvent', 'IEventManager',\
         'IThreadManager', 'IType', 'IHandle', 'ISet', 'IHash', 'IPredicate',\
         'IStateMachine', 'IStateTransition', 'ISubscription']