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

"""This module defines the event thread class that is used to execute
event handlers."""

from threading import Thread
from zope.interface import implements
from boduch.interface import IEventThread

class EventThread(Thread):
    """This class extends the core thread class to start a new thread of
    control."""
    implements(IEventThread)

    def __init__(self, handles):
        """Constructor.  Initialize the thread class as well as the event
        handlers."""
        Thread.__init__(self)
        self.handles=handles
        
    def run(self):
        """Execute each event handler in a new thread."""
        for i in self.handles:
            i.run()
            
__all__=['EventThread']