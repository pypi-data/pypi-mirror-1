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

"""This module defines the core event system functionality."""

from threading import Semaphore
from zope.interface import implements
from boduch.interface import IEventManager
from boduch.event import EventThread
from boduch.type import is_type

class EventManager(object):
    """This class is the core event system.  This is an abstract class and
    there are therefore no instances.  This class defines two class attributes.
    
    The slock attribute is a Semaphore instance from the builtin threading
    Python library.  This lock exists because each time an event is published,
    a new thread of control is started.
    
    The subscriptions attribute is a dictionary containing all event handlers.
    The key of this dictionary is the event class itself."""
    implements(IEventManager)
    slock=Semaphore()
    subscriptions={}
    threaded=False
    
    @classmethod
    def publish(cls, evt, args=[], kw={}):
        """Publish an event.
        
        The evt parameter is the event class to instantiate.  The args 
        parameter and the kw parameter are passed to the event constructor."""
        if cls.subscriptions.has_key(evt):
            params={'event':evt(*args, **kw)}
            handles=cls.build_handlers(evt, params=params)
            if cls.threaded:
                cls.start_event_thread(handles)
            else:
                for i in handles:
                    i.run()
        
    @classmethod
    def subscribe(cls, evt, handle):
        """Subscribe to an event.  The event parameter must inherit from Event
        and the handle parameter must inherit from Handle."""
        if not is_type(evt, "Event"):
            raise TypeError("Invalid event.")
        if not is_type(handle, "Handle"):
            raise TypeError("Invalid handle.")
        if cls.subscriptions.has_key(evt):
            cls.subscriptions[evt].append(handle)
            cls.prioritize(evt)
        else:
            cls.subscriptions[evt]=[handle]
            
    @classmethod
    def unsubscribe(cls, evt, handle):
        """Unsubcribe the specified handler from the specified event."""
        if cls.subscriptions.has_key(evt):
            cnt=0
            for handle_obj in cls.subscriptions[evt]:
                if handle==handle_obj:
                    cls.subscriptions[evt].pop(cnt)
                    return
                cnt+=1
                
    @classmethod
    def prioritize(cls, evt):
        """Prioritize the handlers for the specified event in descending
        order."""
        cls.subscriptions[evt].sort(reverse=True)
                
    @classmethod
    def lock(cls):
        """Acquire the Semaphore lock."""
        if cls.threaded:
            cls.slock.acquire()
        
    @classmethod
    def unlock(cls):
        """Release the Semaphore lock."""
        if cls.threaded:
            cls.slock.release()
            
    @classmethod
    def build_handlers(cls, evt, params={}):
        """Build and return a list of event handlers for the specified 
        event."""
        handlers=[]
        for handler in cls.subscriptions[evt]:
            handlers.append(handler(**params))
        return handlers
          
    @classmethod
    def start_event_thread(cls, handles):
        """Start a new thread of control to run the specified list of event
        handlers in."""
        EventThread(handles).run()
    
__all__=['EventManager']