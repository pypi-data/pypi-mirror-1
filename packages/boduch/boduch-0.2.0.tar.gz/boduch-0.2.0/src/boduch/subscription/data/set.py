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

"""This module defines event subscription instances for Set instances."""

from boduch.event import subscribe, EventSetPush, EventSetSet, EventSetSort,\
                         EventSetPop, EventSetGet
from boduch.handle import HandleSetPush, HandleSetSet, HandleSetSort,\
                          HandleSetPop, HandleSetGet

SubSetPush=subscribe(EventSetPush, HandleSetPush)
SubSetSet=subscribe(EventSetSet, HandleSetSet)
SubSetSort=subscribe(EventSetSort, HandleSetSort)
SubSetPop=subscribe(EventSetPop, HandleSetPop)
SubSetGet=subscribe(EventSetGet, HandleSetGet)

__all__=['SubSetPush', 'SubSetSet', 'SubSetSort', 'SubSetPop', 'SubSetGet']