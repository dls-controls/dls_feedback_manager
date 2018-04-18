#!/bin/env dls-python

import XBPM_feedback_manager
import unittest

## @package dls_feedback_manager
#  Unittests for XBPM Feedback Manager.
#

## Class containing unittest methods.
class FeedbackTests(unittest.TestCase):

    def setUp(self):
        self.shared_PVs = XBPM_feedback_manager.XBPMSharedPVs()
        self.DCM_fdbk = XBPM_feedback_manager.XBPM_DCMFeedback(self.shared_PVs)
        self.FSWT_fdbk = XBPM_feedback_manager.XBPM_FSWTfeedback()

    ## Method to ensure the prefix gets formatted correctly.
    def test_expected_pv_names(self):
        self.assertEqual(self.DCM_fdbk.prefix, 'BL04I-MO-FSWT-01')
        print(self.DCM_fdbk.prefix)
        self.assertEqual(self.FSWT_fdbk.prefix, 'BL04I-MO-FSWT-01')

    def test_validate_params(self):
        self.assertTrue(self.shared_PVs.status_options in range(0,4))

    def test_expected_print_status(self):
        pass

if __name__ == '__main__':
    unittest.main()
