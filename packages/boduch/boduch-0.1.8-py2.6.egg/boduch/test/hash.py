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

"""This module provides a test case for the Hash class and a test
suite that contains the test case."""

import unittest

from boduch.interface import IHash
from boduch.event import Event, publish, subscribe, unsubscribe
from boduch.handle import Handle
from boduch.data import Hash

class TestHash(unittest.TestCase):
    """This class defines the unit tests for the Hash class."""
    def setUp(self):
        """Instantiate the Hash instance to test with."""
        self.hash_obj=Hash()
        self.hash_obj.push(('key', 'value'))
        
    def test_A_interface(self):
        """Testing the Hash interface."""
        self.assertTrue(IHash.implementedBy(Hash),\
                        "IHash not implemented by Hash.")
        self.assertTrue(IHash.providedBy(self.hash_obj),\
                        "IHash not provided by Hash instance.")
                        
    def test_B_push(self):
        """Testing the Hash.push() method."""
        length=len(self.hash_obj.data)
        self.hash_obj.push(('key1', 'value1'))
        self.assertTrue(len(self.hash_obj.data)==(length+1),\
                        "Pushing to the Hash instance failed.")
                  
    def test_C_get(self):
        """Testing the Hash.get() method."""
        result=self.hash_obj.get('key')
        self.assertTrue(result=="value",\
                        "Retrieving from the Hash instance failed.")
            
    def test_D_pop(self):
        """Testing the Hash.pop() method."""
        length=len(self.hash_obj.data)
        self.hash_obj.pop('key')
        self.assertTrue(len(self.hash_obj.data)==(length-1),\
                        "Popping from the Hash instance failed.")
            
    def test_E_setitem(self):
        """Testing the Hash setitem operator."""
        self.hash_obj.push(('key', 'value'))
        self.hash_obj['key']='updated'
        self.assertTrue(self.hash_obj["key"]=="updated",\
                        "The Hash setitem operator failed.")
            
    def test_F_getitem(self):
        """Testing the Hash getitem operator."""
        self.assertTrue(self.hash_obj["key"]=="value",\
                        "The Hash getitem operator failed.")
            
    def test_G_delitem(self):
        """Testing the Hash delitem operator."""
        length=len(self.hash_obj.data)
        del self.hash_obj['key']
        self.assertTrue(len(self.hash_obj.data)==(length-1),\
                        "The Hash delitem operator failed.")
                        
SuiteHash=unittest.TestLoader().loadTestsFromTestCase(TestHash)
            
__all__=['TestHash', 'SuiteHash']
