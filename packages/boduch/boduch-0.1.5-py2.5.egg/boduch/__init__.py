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

"""This package provides some basic tools to assist with common tasks
while developing Python applications.

The event package provides a simple implementation of an event system with
a publish-subscribe architecture."""

from boduch.constant import PRIORITY_CRITICAL, PRIORITY_MAJOR, PRIORITY_MINOR,\
                            PRIORITY_TRIVIAL, TYPE_BOOL, TYPE_BOOLEAN,\
                            TYPE_INT, TYPE_INTEGER, TYPE_LONG, TYPE_FLOAT,\
                            TYPE_STR, TYPE_STRING, TYPE_UNICODE, TYPE_TUPLE,\
                            TYPE_LIST, TYPE_DICT, TYPE_DICTIONARY
from boduch import interface
from boduch import event
from boduch import type
from boduch import handle
from boduch import data
from boduch import predicate
from boduch import state
from boduch import test


__all__=['PRIORITY_CRITICAL', 'PRIORITY_MAJOR', 'PRIORITY_MINOR',\
         'PRIORITY_TRIVIAL', 'TYPE_BOOL', 'TYPE_BOOLEAN', 'TYPE_INT',\
         'TYPE_INTEGER', 'TYPE_LONG', 'TYPE_FLOAT', 'TYPE_STR', 'TYPE_STRING',\
         'TYPE_UNICODE', 'TYPE_TUPLE', 'TYPE_LIST', 'TYPE_DICT',\
         'TYPE_DICTIONARY', 'interface', 'event', 'type', 'handle', 'data',\
         'predicate', 'state', 'test']
__version__='0.1.5'
__author__='Adam Boduch'