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

from zope.interface import Interface, Attribute

class IEventManager(Interface):
    slock=Attribute("""The semaphore lock used for threading.""")
    subscriptions=Attribute("""Stores all event subscriptions.""")
    threaded=Attribute("""True is the event manager is in threaded mode.""")
    
    def publish(cls, evt):
        """Publish the specified event."""
        
    def subscribe(cls, evt, handle):
        """Subscribe the specified handle to the specified event."""
        
    def unsubscribe(cls, evt, handle):
        """Remove the subscription of the specified handle to the specified
        event."""
        
    def prioritize(cls, evt):
        """Sort the list of subscribers to the specified event,
        making the largest handles first."""
        
    def lock(cls):
        """Acquire the Semaphore lock that is owned by the EventManager
        class."""
        
    def unlock(cls):
        """Release the Semaphore lock that is owned by the EventManager
        class."""
        
    def build_handlers(cls, evt, params={}):
        """Build the Handle instances that are currently subcribers to
        the specified event.  The instance is also passed the specified
        keyword parameters."""
        
    def start_event_thread(cls, handles):
        """Start the thread of execution for the specified event handlers."""
    
__all__=['IEventManager']