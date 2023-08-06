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

"""The event package.  The sub-modules defined in this package are all related
to implementing an event-based system."""

from boduch.event.eventthread import EventThread
from boduch.event.event import Event
from boduch.event.threadmanager import ThreadManager
from boduch.event.eventmanager import EventManager
from boduch.event.util import publish, subscribe, unsubscribe, threaded
from boduch.event.data import EventSetPush, EventSetPop, EventSetSort,\
                              EventSetGet, EventSetSet, EventHashPush,\
                              EventHashPop, EventHashGet
from boduch.event.predicate import EventEqual, EventGreater, EventLesser

__all__=['Event', 'EventManager', 'EventThread',\
         'ThreadManager', 'publish', 'subscribe', 'unsubscribe', 'threaded',\
         'EventSetPush', 'EventSetPop', 'EventSetGet',\
         'EventSetSort', 'EventHashPush', 'EventHashPop', 'EventHashGet',\
         'EventEqual', 'EventGreater', 'EventLesser']