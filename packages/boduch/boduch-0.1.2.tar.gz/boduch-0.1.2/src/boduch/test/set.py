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
        
    def test_A_interface(self):
        """Test the Set instaface."""
        self.assertTrue(ISet.implementedBy(Set),\
                        'ISet not implemented by Set.')
        self.assertTrue(ISet.providedBy(self.set_obj),\
                        'ISet not provided by Set instance.')
                        
    def test_B_push(self):
        """Test the Set.push() method."""
        try:
            self.set_obj.push('test')
        except Exception, e:
            self.fail(str(e))
            
    def test_C_sort(self):
        """Test the Set.sort() method."""
        try:
            self.set_obj.sort()
        except Exception, e:
            self.fail(str(e))
        
    def test_D_get(self):
        """Test the Set.get() method."""
        try:
            self.set_obj.get(0)
        except Exception, e:
            self.fail(str(e))
            
    def test_E_pop(self):
        """Test the Set.pop() method."""
        try:
            self.set_obj.pop(0)
        except Exception, e:
            self.fail(str(e))
            
    def test_F_setitem(self):
        """Test the setitem operator."""
        try:
            self.set_obj.push('test')
            self.set_obj[0]='testing'
        except Exception, e:
            self.fail(str(e))
            
    def test_G_getitem(self):
        """Test the getitem operator."""
        try:
            self.set_obj[0]
        except Exception, e:
            self.fail(str(e))
            
    def test_H_delitem(self):
        """Test the delitem operator."""
        try:
            del self.set_obj[0]
        except Exception, e:
            self.fail(str(e))
            
    def test_I_iteritem(self):
        """Test the iteritem operator."""
        self.set_obj.push('test')
        try:
            for i in self.set_obj:
                pass
        except Exception, e:
            self.fail(str(e))
             
SuiteSet=unittest.TestLoader().loadTestsFromTestCase(TestSet)

__all__=['TestSet', 'SuiteSet']            
                        