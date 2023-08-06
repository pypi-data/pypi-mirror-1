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

"""This module defines the basic event interface."""

from zope.interface import Interface, Attribute

class IEvent(Interface):
    """This interface is for the basic event type.  It is really meant as an
    indicator that the derived event classes are actually events."""
    time=Attribute("""The time the event occurred at.""")
    
    def get_time(self):
        """Return the time this event occured."""
    
__all__=['IEvent']