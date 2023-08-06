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

"""This module provides a test case for the Set class and a test
suite which contains a the test case class."""

import unittest

from boduch.interface import ISet
from boduch.event import Event, publish, subscribe, unsubscribe
from boduch.handle import Handle
from boduch.data import Set

class TestSet(unittest.TestCase):
    """This class is the test case for Set instances."""
    def setUp(self):
        """Create the test Set instance."""
        self.set_obj=Set()
        self.set_obj.push(0)
        
    def test_A_interface(self):
        """Testing the Set instaface."""
        self.assertTrue(ISet.implementedBy(Set),\
                        "ISet not implemented by Set.")
        self.assertTrue(ISet.providedBy(self.set_obj),\
                        "ISet not provided by Set instance.")
                        
    def test_B_push(self):
        """Testing the Set.push() method."""
        length=len(self.set_obj.data)
        self.set_obj.push("test")
        self.assertTrue(len(self.set_obj.data)==(length+1),\
                        "Pushing to the Set instance failed.")
            
    def test_C_sort(self):
        """Testing the Set.sort() method."""
        self.set_obj.push(5)
        self.set_obj.push(4)
        self.set_obj.sort()
        self.assertTrue(self.set_obj[len(self.set_obj.data)-1]==5,\
                        "Sorting the Set instance failed.")
        
    def test_D_get(self):
        """Testing the Set.get() method."""
        val="test"
        self.set_obj.push(val)
        self.assertTrue(self.set_obj[len(self.set_obj.data)-1]==val,\
                        "Getting from the Set instance failed.")
            
    def test_E_pop(self):
        """Testing the Set.pop() method."""
        length=len(self.set_obj.data)
        self.set_obj.pop(0)
        self.assertTrue(len(self.set_obj.data)==(length-1),\
                        "Popping from the Set instance failed.")
            
    def test_F_setitem(self):
        """Testing the setitem operator."""
        self.set_obj[0]="setitem"
        self.assertTrue(self.set_obj[0]=="setitem",\
                        "The Set setitem operator failed.")
            
    def test_G_getitem(self):
        """Testing the getitem operator."""
        self.assertTrue(self.set_obj[0]==0,\
                        "The Set getitem operator failed.")
            
    def test_H_delitem(self):
        """Testing the delitem operator."""
        length=len(self.set_obj.data)
        del self.set_obj[0]
        self.assertTrue(len(self.set_obj.data)==(length-1),\
                        "The Set delitem operator failed.")
            
    def test_I_iteritem(self):
        """Testing the iteritem operator."""
        self.set_obj.push('test')
        cnt=0
        for i in self.set_obj:
            cnt+=1
        self.assertTrue(len(self.set_obj.data)==cnt,\
                        "The Set iteritem operator failed.")
             
SuiteSet=unittest.TestLoader().loadTestsFromTestCase(TestSet)

__all__=['TestSet', 'SuiteSet']            
                        