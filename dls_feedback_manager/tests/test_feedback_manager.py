#!/bin/env dls-python

import unittest
import XBPM_feedback_manager

## @package dls_feedback_manager
#  Unittests for XBPM Feedback Manager.
#

## Class containing unittest methods.
class FeedbackTests(unittest.TestCase):

    def setUp(self):
        self.shared_PVs = XBPM_feedback_manager.XBPMSharedPVs('04')
        self.XBPM1_fdbk = XBPM_feedback_manager.XBPM1_feedback(self.shared_PVs, 'BL04I-MO-DCM-01')
        self.XBPM2_fdbk = XBPM_feedback_manager.XBPM2_feedback(self.shared_PVs, 'BL04I-MO-FSWT-01', '')

    ## Method to ensure the prefix gets formatted correctly.
    def test_prefix(self):
        self.assertEqual(self.XBPM1_fdbk.prefix, 'BL04I-MO-FSWT-01')
        print("xbpm1 prefix is " + self.XBPM1_fdbk.prefix)
        self.assertEqual(self.XBPM2_fdbk.prefix, 'BL04I-MO-FSWT-01')

    def test_xbpm_fbcheck_name(self):
        self.assertTrue('FE04I-PS-SHTR-02:STA' in self.XBPM2_fdbk.xbpm_fbcheck)

    def test_validate_status_options(self):
        self.assertTrue(self.shared_PVs.status_options in range(0, 4))

    def test_reset_when_fb_off(self):
        pass

    def test_restart_pid_params(self):  # is this necessary
        pass

    def test_enable_button(self):
        pass  # on or off, test prints under different circumstances

    def test_XBPM2_PID_limits(self):
        pass  # redefine e.g. kpx2 and make sure its inside lopr and hopr


# RESET EVERYTHING BACK TO CERTAIN CONFIGURATION WHEN IOC TURNED OFF
# RESET BEFORE RERUNNING TESTS

    """def test_example_of_setup_name(self):
        pass

    def test_expected_print_status(self):
        pass

    def test_check_feedback_inputs(self):
        pass

    def test_check_enable_status(self):
        pass

    def test_enable_status_checker(self):
        pass
    """

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
