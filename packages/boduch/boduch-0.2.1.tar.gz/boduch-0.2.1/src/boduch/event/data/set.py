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

"""This module defines events related to the data.Set data type."""

from boduch.event import Event

class EventSetPush(Event):
    """Event that is published by the Set.push() method."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventSetPop(Event):
    """Event that is published by the Set.pop() method."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventSetGet(Event):
    """Event that is published by the Set.get() method."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventSetSet(Event):
    """Event that is published by the Set.set() method."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
class EventSetSort(Event):
    """Event that is published by the Set.sort() method."""
    def __init__(self, *args, **kw):
        Event.__init__(self, *args, **kw)
        
__all__=['EventSetPush', 'EventSetPop', 'EventSetGet', 'EventSetSet',\
         'EventSetSort']