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

from threading import Semaphore
from zope.interface import implements
from boduch.interface import ILockManager
from boduch.event import ThreadManager

class LockManager(object):
    implements(ILockManager)
    slock=Semaphore()
    
    @classmethod
    def get_slock(cls):
        """Return the Semaphore lock associated with the lock manager."""
        return cls.slock
    
    @classmethod
    def lock(cls):
        """Acquire the Semaphore lock."""
        if ThreadManager.get_threaded():
            cls.get_slock().acquire()
        
    @classmethod
    def unlock(cls):
        """Release the Semaphore lock."""
        if ThreadManager.get_threaded():
            cls.get_slock().release()
            
__all__=['LockManager']