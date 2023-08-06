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

"""This module defines the interface provided by the base event handler."""

from zope.interface import Interface, Attribute

class IHandle(Interface):
    """This is the base event handler interface.  All handlers must define
    a run method."""
    def run(self):
        """Execute the event handler."""
        
    def get_event(self):
        """Return the event associated with this handle."""
    
__all__=['IHandle']