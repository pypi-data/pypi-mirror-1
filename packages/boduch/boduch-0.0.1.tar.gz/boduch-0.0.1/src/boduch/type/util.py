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

def is_type(obj, type):
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
    return type in candidates

__all__=['is_type']
