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

"""This module provides a test case class for testing events called
TestEvent and a test suite which contains the event test case class."""

import unittest

from boduch.interface import IEvent
from boduch.event import Event, publish, subscribe, unsubscribe
from boduch.handle import Handle

class TestEvent(unittest.TestCase):
    """This class is derived from the TestCase class which is part of the
    builtin unittest Python module.  There are several methods defined by
    this class each representing some area of event testing."""
    def setUp(self):
        """This method is invoked before any tests are run.  Here we create
        a test event instance which is a attribute of the TestEvent class.
        This instance is then available to the remaining methods defined in
        this class."""
        self.test_event_obj=Event()
        
    def test_A_interface(self):
        """Perform some event interface tests.  First, we verify that the 
        Event class implements the IEvent interface and the test event 
        instance provides the IEvent interface."""
        self.assertTrue(IEvent.implementedBy(Event),\
                        'IEvent not implemented by Event.')
        self.assertTrue(IEvent.providedBy(self.test_event_obj),\
                        'IEvent not provided by Event instance.')
                        
    def test_B_subscribe(self):
        """Perform a subscribe test.  Here, we simply subscribe a basic
        handler to handle a basic event."""
        try:
            subscribe(Event, Handle)
        except Exception, e:
            self.fail(str(e))
            
    def test_C_publish(self):
        """Perform a publish test.  Here, we publish a simple event."""
        try:
            publish(Event)
        except NotImplementedError:
            pass
        except Exception, e:
            self.fail(str(e))
                        
SuiteEvent=unittest.TestLoader().loadTestsFromTestCase(TestEvent)

__all__=['TestEvent', 'SuiteEvent']