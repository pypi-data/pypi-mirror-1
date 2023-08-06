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

"""This module contains a utility function for executing all the test
suites."""

import unittest

from boduch.test import SuiteEvent, SuiteSet, SuiteHash, SuitePredicate
from boduch.event import threaded

def run_tests(is_threaded=False):
    """This function creates a test suite, adds all other suites to it, and
    runs the tests."""
    threaded(is_threaded)
    MainTestSuite=unittest.TestSuite()
    MainTestSuite.addTest(SuiteEvent)
    MainTestSuite.addTest(SuiteSet)
    MainTestSuite.addTest(SuiteHash)
    MainTestSuite.addTest(SuitePredicate)
    unittest.TextTestRunner(verbosity=2).run(MainTestSuite)
    
__all__=['run_tests']