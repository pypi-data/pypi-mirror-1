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

"""This module defines the interface for the base type class."""

from zope.interface import Interface, Attribute

class IType(Interface):
    data=Attribute("""The data dictionary associated with the type.""")
    uuid=Attribute("""The uuid of this type.""")
    
    """The base type class defines several operator-overloading methods."""
    def __len__(self):
        """Needed to compute the length of an instance."""
        
    def __eq__(self, other):
        """Needed for instance equivalence comparison."""
        
    def __lt__(self, other):
        """Needed for instance less than comparison."""
        
    def __gt__(self, other):
        """Needed for instance greater than comparison."""
        
    def __cmp__(self, other):
        """Needed for instance sorting comparison."""
        
__all__=['IType']