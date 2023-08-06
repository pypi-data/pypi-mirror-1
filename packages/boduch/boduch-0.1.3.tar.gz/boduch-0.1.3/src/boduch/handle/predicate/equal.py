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

from boduch.handle import Handle
from boduch import PRIORITY_CRITICAL

class HandleEqual(Handle):
    def __init__(self, *args, **kw):
        Handle.__init__(self, *args, **kw)
        self.priority=PRIORITY_CRITICAL
        
    def run(self):
        event_obj=self.data['event']
        predicate_obj=event_obj.data['predicate']
        lop, rop=predicate_obj.invoke_operators()
        predicate_obj.result=lop==rop
        
__all__=['HandleEqual']