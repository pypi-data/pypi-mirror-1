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

"""This package defines constants used in the boduch Python library."""

from boduch.constant.priority import PRIORITY_CRITICAL, PRIORITY_MAJOR,\
                                     PRIORITY_MINOR, PRIORITY_TRIVIAL
from boduch.constant.type import TYPE_BOOL, TYPE_BOOLEAN, TYPE_INT,\
                                 TYPE_INTEGER, TYPE_LONG, TYPE_FLOAT,\
                                 TYPE_STR, TYPE_STRING, TYPE_UNICODE,\
                                 TYPE_TUPLE, TYPE_LIST, TYPE_DICT,\
                                 TYPE_DICTIONARY
                                    
__all__=['PRIORITY_CRITICAL', 'PRIORITY_MAJOR', 'PRIORITY_MINOR',\
         'PRIORITY_TRIVIAL', 'TYPE_BOOL', 'TYPE_BOOLEAN', 'TYPE_INT',\
         'TYPE_INTEGER', 'TYPE_LONG', 'TYPE_FLOAT', 'TYPE_STR',\
         'TYPE_STRING', 'TYPE_UNICODE', 'TYPE_TUPLE', 'TYPE_LIST',\
         'TYPE_DICT', 'TYPE_DICTIONARY']