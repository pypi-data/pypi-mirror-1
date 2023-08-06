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

"""This package contains test cases and test suites for the boduch
Python library."""

from boduch.test.event import TestEvent, SuiteEvent
from boduch.test.set import TestSet, SuiteSet
from boduch.test.hash import TestHash, SuiteHash
from boduch.test.predicate import TestPredicate, SuitePredicate
from boduch.test.state import TestState, SuiteState
from boduch.test.util import run_tests

__all__=['TestEvent', 'TestSet', 'TestHash', 'TestPredicate', 'TestState',\
         'SuiteEvent', 'SuiteSet', 'SuiteHash', 'SuitePredicate',\
         'SuiteState' 'run_tests']
