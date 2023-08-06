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

"""This module defines some simple utility type functionality."""

import types
from boduch.constant import *

def is_type(obj, t):
    """Return true if the specified obj is the specified type."""
    candidates=[]
    if hasattr(obj, '__name__'):
        candidates.append(obj.__name__)
    elif hasattr(obj, '__class__'):
        class_obj=obj.__class__
        candidates.append(class_obj.__name__)
        for base in class_obj.__bases__:
            candidates.append(base.__name__)
    if hasattr(obj, '__bases__'):
        for base in obj.__bases__:
            candidates.append(base.__name__)
    if t in candidates:
        return True
    else:
        t=t.upper()
        if t==TYPE_BOOL or t==TYPE_BOOLEAN:
            return type(obj) is types.BooleanType
        elif t==TYPE_INT or t==TYPE_INTEGER:
            return type(obj) is types.IntType
        elif t==TYPE_LONG:
            return type(obj) is types.LongType
        elif t==TYPE_FLOAT:
            return type(obj) is types.FloatType
        elif t==TYPE_STR or t==TYPE_STRING:
            return type(obj) is types.StringType
        elif t==TYPE_UNICODE:
            return type(obj) is types.UnicodeType
        elif t==TYPE_TUPLE:
            return type(obj) is types.TupleType
        elif t==TYPE_LIST:
            return type(obj) is types.ListType
        elif t==TYPE_DICT or t==TYPE_DICTIONARY:
            return type(obj) is types.DictionaryType

__all__=['is_type']
