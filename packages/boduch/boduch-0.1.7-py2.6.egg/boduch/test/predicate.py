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

from boduch.predicate import Predicate, Equal, Greater, Lesser
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
                        
    def test_B_equal_true(self):
        """Testing the Equal predicate is true"""
        self.assertTrue(Equal(1,1))
        
    def test_C_equal_false(self):
        """Testing the Equal predicate is false"""
        self.assertFalse(Equal(1,2))
        
    def test_D_greater_true(self):
        """Tesing the Greater predicate is true"""
        self.assertTrue(Greater(2,1))
        
    def test_E_greater_false(self):
        """Testing the Greater predicate is false"""
        self.assertFalse(Greater(1,2))
        
    def test_F_lesser_true(self):
        """Testing the Lesser predicate is true"""
        self.assertTrue(Lesser(1,2))
        
    def test_G_lesser_false(self):
        """Testing the Lesser predicate is false"""
        self.assertFalse(Lesser(2,1))
                        
SuitePredicate=unittest.TestLoader().loadTestsFromTestCase(TestPredicate)
            
__all__=['TestPredicate', 'SuitePredicate']