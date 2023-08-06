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

class IThreadManager(Interface):
    threaded=Attribute("""True if the thread manager is running in threaded
    mode.""")
    max_threads=Attribute("""Maximum number of threads that can run.""")
    
    def get_threaded(cls):
        """Return true if the thread manager is running in threaded mode."""
 
    def start_event_thread(cls, queue):
        """Start a new thread of control to run the first handle found in 
        the specified queue."""
        
__all__=['IThreadManager']