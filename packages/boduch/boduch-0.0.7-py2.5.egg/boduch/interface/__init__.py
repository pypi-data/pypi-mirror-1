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

from boduch.interface.eventthread import IEventThread
from boduch.interface.event import IEvent
from boduch.interface.eventmanager import IEventManager
from boduch.interface.lockmanager import ILockManager
from boduch.interface.type import IType
from boduch.interface.handle import IHandle
from boduch.interface.set import ISet
from boduch.interface.hash import IHash

__all__=['IEventThread', 'IEvent', 'IEventManager', 'ILockManager', 'IType',\
         'IHandle', 'ISet', 'IHash']