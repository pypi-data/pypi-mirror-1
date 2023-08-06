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

"""This module defines some utility functions that are designed to make
using the event system slightly easier."""

from boduch.event import EventManager, ThreadManager

def publish(evt, args=[], kw={}, atomic=False):
    """Make a publish event call to the event manager."""
    EventManager.publish(evt, args=args, kw=kw, atomic=atomic)
    
def subscribe(evt, handle):
    """Make a subcribe to event call to the event manager."""
    EventManager.subscribe(evt, handle)
    
def unsubscribe(evt, handle):
    """Make a unsubscribe to event call to the event manager."""
    EventManager.unsubscribe(evt, handle)
    
def threaded(is_threaded):
    """Set the mode of the event manager.  True for threaded mode."""
    ThreadManager.threaded=is_threaded
    
__all__=['publish', 'subscribe', 'unsubscribe', 'threaded']