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

import unittest

from boduch.predicate import Predicate, Equal
from boduch.interface import IPredicate

class TestPredicate(unittest.TestCase):
    def setUp(self):
        self.predicate_obj=Predicate(False, False)
        
    def test_A_interface(self):
        """Testing the Predicate interface"""
        self.assertTrue(IPredicate.implementedBy(Predicate),\
                        'IPredicate not implemented by Predicate.')
        self.assertTrue(IPredicate.providedBy(self.predicate_obj),\
                        'IPredicate not provided by Predicate instance.')
                        
    def test_B_equal(self):
        """Testing the Equal predicate"""
        self.assertTrue(Equal(1,1))
                        
SuitePredicate=unittest.TestLoader().loadTestsFromTestCase(TestPredicate)
            
__all__=['TestPredicate', 'SuitePredicate']