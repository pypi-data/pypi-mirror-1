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

"""This module defines the ThreadManager class."""

from zope.interface import implements
from boduch.interface import IThreadManager
from boduch.event import EventThread, build_thread_class

class ThreadManager:
    """The ThreadManager is responsible for starting new event threads.
    Event threads are threads where handles are executed.
    
    The threaded attribute indicates if threading is actually enabled.
    
    The max_threads attribute indicates how many threads are allowed to
    run concurrently."""
    implements(IThreadManager)
    threaded=False
    processed=False
    
    @classmethod
    def get_threaded(cls):
        """Return true if the thread manager is running in threaded mode."""
        return cls.threaded
    
    @classmethod
    def get_processed(cls):
        """Return true if the thread manager is running in processed mode."""
        return cls.processed
    
    @classmethod
    def start_event_thread(cls, queue):
        """Start a new thread of control to run the first encountered handle
        in the specified queue."""
        EventThread=build_thread_class(threaded=cls.threaded, processed=cls.processed)
        EventThread(queue).start()
    
__all__=['ThreadManager']