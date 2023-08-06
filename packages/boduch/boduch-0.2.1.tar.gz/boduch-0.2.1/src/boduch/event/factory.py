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

from Queue import Empty
from zope.interface import implements
from boduch.type import Type
from boduch.interface import IEventThread
#from boduch.event import ThreadManager

def build_thread_base_class(threaded=False, processed=False):
    if threaded:
        from threading import Thread
        return Thread
    elif processed:
        from multiprocessing import Process
        return Process
    
def build_thread_class(threaded=False, processed=False):
    Thread=build_thread_base_class(threaded=threaded, processed=processed)
    class EventThread(Type, Thread):
        """This class extends the core thread class to start a new thread of
        control."""
        implements(IEventThread)

        def __init__(self, queue):
            """Constructor.  Initialize the thread class as well as the event
            queue."""
            Type.__init__(self)
            Thread.__init__(self, name=self.uuid)
            self.queue=queue
            
        def run(self):
            """Execute each event handler in a new thread."""
            while True:
                try:
                    handle=self.queue.get_nowait()
                    handle.run()
                except Empty:
                    break
    return EventThread
    
__all__=["build_thread_base_class", "build_thread_class"]