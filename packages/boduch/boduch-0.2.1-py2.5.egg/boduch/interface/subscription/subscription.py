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

class ISubscription(Interface):
    """The event subscription interface."""
    event=Attribute("""The event of the subscription.""")
    handle=Attribute("""The handle of the subscription.""")
    
    def subscribe(self, handle):
        """Subscribe the specified handle to the event held by this
        subscription."""
        self.event.subscribe(handle)
        
    def unsubscribe(self, handle):
        """Unsubscribe the specified handle from the event held by this
        subscription."""
        self.event.unsubscribe(handle)
    
__all__=['ISubscription']