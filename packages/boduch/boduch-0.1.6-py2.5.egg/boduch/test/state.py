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

from boduch.interface import IStateMachine, IStateTransition
from boduch.state import StateMachine, StateTransition

class TestState(unittest.TestCase):
    def setUp(self):
        self.test_machine_obj=StateMachine()
        self.test_transition_obj=StateTransition()
        
    def test_A_machine_interface(self):
        self.assertTrue(IStateMachine.implementedBy(StateMachine),\
                        'IStateMachine not implemented by StateMachine.')
        self.assertTrue(IStateMachine.providedBy(self.test_machine_obj),\
                        'IStateMachine not provided by StateMachine instance.')
                        
    def test_B_transition_interface(self):
        self.assertTrue(IStateTransition.implementedBy(StateTransition),\
                        'IStateTransition not implemented by StateTransition.')
        self.assertTrue(IStateTransition.providedBy(self.test_transition_obj),\
                        'IStateTransition not provided by instance.')
                        
    def test_C_machine_add_state(self):
        try:
            self.test_machine_obj.add_state("RUNNING")
        except Exception, e:
            self.fail(str(e))
        
    def test_D_machine_remove_state(self):
        self.test_machine_obj.add_state("RUNNING")
        try:
            self.test_machine_obj.remove_state("RUNNING")
        except Exception, e:
            self.fail(str(e))
            
    def test_E_machine_change_state(self):
        self.test_machine_obj.add_state("RUNNING")
        try:
            self.test_machine_obj.change_state("RUNNING")
        except Exception, e:
            self.fail(str(e))
            
SuiteState=unittest.TestLoader().loadTestsFromTestCase(TestState)

__all__=['TestState', 'SuiteState']