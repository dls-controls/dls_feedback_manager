#!/bin/env dls-python

import XBPM_range_manager
import unittest

class RangeTests(unittest.TestCase):

    def setUp(self):
        self.XBPM1 = XBPM_range_manager.range_manager('BL04I-EA-XBPM-', '01', 90e-9, 110e-9, 1.0, 3.0)
        self.XBPM2 = XBPM_range_manager.range_manager('BL04I-EA-XBPM-', '02', 90e-9, 110e-9, 3.2, 3.0)

    def test_standard_naming(self):
    # Test output for one of them to check it's got the correct name/nums
        self.assertEqual(self.XBPM1.XBPM_prefix+self.XBPM1.XBPM_num, 'BL04I-EA-XBPM-01')
        self.assertEqual(self.XBPM1.lower_current_limit, 90e-9)
        self.assertNotEqual(self.XBPM1.lower_current_limit, 0.0)
        self.assertEqual(self.XBPM1.XBPM_num, '01')

    def test_regular_expression(self):
        self.XBPM = XBPM_range_manager.range_manager('BL04I-EA-XBPM-', '00', 1, 2, 3, 4)
        self.assertRegexpMatches(self.XBPM.XBPM_prefix+self.XBPM1.XBPM_num, "BL04I-EA-XBPM-01")

    def test_initial_variable_inputs(self):
        # Floats only for now, change if putting string names of PVs
        self.assertRaises(AssertionError, XBPM_range_manager.range_manager('BL04I-EA-XBPM-', '01', 1, 11, "-9", 40.0)

    def test_invalid_threshold_percentage(self):
        self.assertRaises(AssertionError, XBPM_range_manager.range_manager('BL04I-EA-XBPM-', '01', 90e-9, 110e-9, 1.0, -84))

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



