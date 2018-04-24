#!/bin/env dls-python

import unittest
import XBPM_feedback_manager

## @package dls_feedback_manager
#  Unittests for XBPM Feedback Manager.
#

## Class containing unittest methods.
class FeedbackTests(unittest.TestCase):

    def setUp(self):
        self.shared_PVs = XBPM_feedback_manager.XBPMSharedPVs()
        self.XBPM1_fdbk = XBPM_feedback_manager.XBPM1_Feedback(self.shared_PVs, self.xbpm1_prefix)
        self.XBPM2_fdbk = XBPM_feedback_manager.XBPM2_Feedback(self.shared_PVs, self.xbpm2_prefix)

    ## Method to ensure the prefix gets formatted correctly.
    def test_expected_pv_names(self):
        self.assertEqual(self.XBPM1_fdbk.prefix, 'BL04I-MO-FSWT-01')
        print("DCM prefix is " + self.XBPM1_fdbk.prefix)
        self.assertEqual(self.XBPM2_fdbk.prefix, 'BL04I-MO-FSWT-01')

    def test_validate_status_options(self):
        self.assertTrue(self.shared_PVs.status_options in range(0, 4))

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
