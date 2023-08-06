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

"""This package contains basic event handlers."""

from boduch.event import subscribe, EventSetPush, EventSetSet, EventSetSort,\
                         EventSetPop, EventSetGet, EventHashPush,\
                         EventHashPop, EventHashGet, EventEqual, EventGreater,\
                         EventLesser
from boduch.handle.handle import Handle
from boduch.handle.data import HandleHashPush, HandleHashPop, HandleHashGet,\
                               HandleSetPush, HandleSetSet, HandleSetSort,\
                               HandleSetPop, HandleSetGet
from boduch.handle.predicate import HandleEqual, HandleGreater, HandleLesser

subscribe(EventSetPush, HandleSetPush)
subscribe(EventSetSet, HandleSetSet)
subscribe(EventSetSort, HandleSetSort)
subscribe(EventSetPop, HandleSetPop)
subscribe(EventSetGet, HandleSetGet)
subscribe(EventHashPush, HandleHashPush)
subscribe(EventHashPop, HandleHashPop)
subscribe(EventHashGet, HandleHashGet)
subscribe(EventEqual, HandleEqual)
subscribe(EventGreater, HandleGreater)
subscribe(EventLesser, HandleLesser)

__all__=['Handle', 'HandleSetPush', 'HandleSetSet', 'HandleSetSort',\
         'HandleSetPop', 'HandleSetGet', 'HandleHashPush', 'HandleHashPop',\
         'HandleHashGet', 'HandleEqual', 'HandleGreater', 'HandleLesser']