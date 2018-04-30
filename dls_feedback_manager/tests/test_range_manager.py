#!/bin/env dls-python

import XBPM_range_manager
import unittest
import re

## @package dls_feedback_manager
# Unittests for XBPM Range Manager.

## Class containing unittest methods for the range/scale.
class RangeTests(unittest.TestCase):

    ## Setup method with parameters for XBPM1 and XBPM2
    #  See XBPM_range_manager for definitions of each parameter.
    def setUp(self):
        self.XBPM1 = XBPM_range_manager.RangeManager('BL04I-EA-XBPM-', '01', 90e-9, 110e-9, 1.0, 3.0)
        self.XBPM2 = XBPM_range_manager.RangeManager('BL04I-EA-XBPM-', '02', 90e-9, 110e-9, 3.2, 3.0)

    ## Method to ensure PV name combines correctly.
    #  Parameters are defined using user input values in XBPM_manager_control.
    def test_standard_naming(self):
        self.assertEqual(self.XBPM1.xbpm_prefix+self.XBPM1.xbpm_num, 'BL04I-EA-XBPM-01')
        self.assertEqual(self.XBPM1.lower_current_limit, 90e-9)
        self.assertNotEqual(self.XBPM1.lower_current_limit, 0.0)
        self.assertEqual(self.XBPM1.xbpm_num, '01')

    ## Expected format for PV name
    def test_regular_expression(self):
        XBPM = XBPM_range_manager.RangeManager('BL04I-EA-XBMP-', '02', 1, 2, 3, 4)
        self.assertRegexpMatches(XBPM.xbpm_prefix+XBPM.xbpm_num, "BL04I-EA-XBPM-01")

    ## Error is raised as XBPM number is not between 1 and 9
    def test_XBPM_num(self):
        XBPM = XBPM_range_manager.RangeManager('BL04I-EA-XBPM-', '00', 1, 2, 3, 4)
        self.assertRaises(AssertionError, XBPM.xbpm_num)

    ## Makes sure error is raised when incorrect value for scale factor is set.
    def test_initial_variable_inputs(self):
        self.assertRaises(AssertionError, XBPM_range_manager.RangeManager('BL04I-EA-XBPM-', '01', 1, 11, "-9", 40.0))

    ## Error is raised when threshold percentage is outside of range (0-100)
    def test_invalid_threshold_percentage(self):
        self.assertRaises(AssertionError, XBPM_range_manager.RangeManager('BL04I-EA-XBPM-', '01', 90e-9, 110e-9, 1.0, -84))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()



"""def test_camonitor_range(self):
    #how
        pass

    def test_check_range(self):
    # how
        pass

    def test_camonitor_scale(self):
        # how
        pass

    def test_curr_limits(self):
    #   Initial value is between LOPR/HOPR
        pass

    def test_signals_ok(self):
    # Name combines properly
        pass

    def test_not_none(self):
    # No fields left empty
        pass """



