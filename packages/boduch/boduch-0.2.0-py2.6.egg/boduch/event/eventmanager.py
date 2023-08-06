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

from Queue import Queue
from zope.interface import implements
from boduch.interface import IEventManager
from boduch.event import ThreadManager
from boduch.subscription import Subscription
from boduch.type import is_type

def sort_object_list(seq, attr):
    intermed = [ (getattr(seq[i],attr), i, seq[i]) for i in xrange(len(seq)) ]
    intermed.sort(reverse=True)
    return [ tup[-1] for tup in intermed ]

class EventManager(object):
    """This class is the core event system.  This is an abstract class and
    there are therefore no instances.  This class defines two class attributes.
    
    The queue attribute is where Handle instances are placed when running in
    threaded mode.  Event threads then consume handles from the queue.
    
    The subscriptions attribute is a dictionary containing all event handlers.
    The key of this dictionary is the event class itself."""
    implements(IEventManager)
    subscriptions={}
    queue=Queue(0)
    
    @classmethod
    def get_subscriptions(cls, evt=None):
        """Return the handle instances that are subscribed to the specified
        event.  If the event is not specified, return all handles."""
        if evt and cls.subscriptions.has_key(evt):
            return cls.subscriptions[evt]
        return cls.subscriptions
    
    @classmethod
    def publish(cls, evt, args=[], kw={}, atomic=False):
        """Publish an event.
        
        The evt parameter is the event class to instantiate.  The args 
        parameter and the kw parameter are passed to the event constructor.
        
        If the atomic parameter is true, any subscribed to the event will
        execute synchronously in this thread."""
        if cls.get_subscriptions().has_key(evt):
            params={'event':evt(*args, **kw)}
            handles=cls.build_handlers(evt, params=params)
            if ThreadManager.get_threaded() and not atomic:
                for handle in handles:
                    cls.queue.put(handle)
                    ThreadManager.start_event_thread(cls.queue)
            else:
                for handle in handles:
                    handle.run()
        
    @classmethod
    def subscribe(cls, evt, handle):
        """Subscribe to an event.  The event parameter must inherit from Event
        and the handle parameter must inherit from Handle."""
        if not is_type(evt, "Event"):
            raise TypeError("Invalid event.")
        if not is_type(handle, "Handle"):
            raise TypeError("Invalid handle.")
        if cls.get_subscriptions().has_key(evt):
            if handle not in cls.get_subscriptions(evt=evt):
                cls.subscriptions[evt].append(handle)
                cls.prioritize(evt)
        else:
            cls.subscriptions[evt]=[handle]
            cls.prioritize(evt)
        return Subscription(evt, handle)
            
    @classmethod
    def unsubscribe(cls, evt, handle):
        """Unsubcribe the specified handler from the specified event."""
        if cls.get_subscriptions().has_key(evt):
            cnt=0
            for handle_obj in cls.get_subscriptions(evt=evt):
                if handle==handle_obj:
                    cls.subscriptions[evt].pop(cnt)
                    return
                cnt+=1
                
    @classmethod
    def prioritize(cls, evt):
        """Prioritize the handlers for the specified event in descending
        order.  This means that handles that evaluate to a higher integer
        value, they will execute first for an given event."""
        cls.subscriptions[evt]=sort_object_list(cls.subscriptions[evt],\
                                                "priority")

    @classmethod
    def build_handlers(cls, evt, params={}):
        """Build and return a list of event handlers for the specified 
        event."""
        handlers=[]
        for handler in cls.get_subscriptions(evt=evt):
            handlers.append(handler(**params))
        return handlers
    
__all__=['EventManager']