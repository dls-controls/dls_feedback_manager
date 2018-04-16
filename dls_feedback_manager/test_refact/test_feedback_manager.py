#!/bin/env dls-python

import XBPM_feedback_manager
import unittest

## @package dls_feedback_manager
#  Unittests for XBPM Feedback Manager.
#

## Class containing unittest methods.
class FeedbackTests(unittest.TestCase):

    ## Method to ensure the prefix is formatted correctly.
    def test_expected_pv_names(self):
        self.assertEqual(XBPM_feedback_manager.XBPM_DCMFeedback.__init__(self.prefix), 'BL04I-MO-FSWT-01')
        self.assertEqual(XBPM_feedback_manager.XBPM_FSWTfeedback.__init__(self.prefix), 'BL04I-MO-FSWT-01')

    def test_expected_print_status(self):
        pass

if __name__ == '__main__':
    unittest.main()
