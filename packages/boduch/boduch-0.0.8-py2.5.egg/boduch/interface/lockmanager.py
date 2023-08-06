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

class ILockManager(Interface):
    slock=Attribute("""The semaphore lock used for threading.""")
    
    def get_slock(cls):
        """Return the event manager Semaphore lock."""
        
    def lock(cls):
        """Acquire the Semaphore lock that is owned by the EventManager
        class."""
        
    def unlock(cls):
        """Release the Semaphore lock that is owned by the EventManager
        class."""
        
__all__=['ILockManager']