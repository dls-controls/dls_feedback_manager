#!/bin/env dls-python

import XBPM_feedback_manager
import unittest

class FeedbackTests(unittest.TestCase):

    def test_expected_pv_names(self):
        self.assertEqual(XBPM_feedback_manager.XBPM_DCMFeedback.__init__(self.prefix), 'BL04I-MO-FSWT-01')
        self.assertEqual(XBPM_feedback_manager.XBPM_FSWTfeedback.__init__(self.prefix), 'BL04I-MO-FSWT-01')

    def test_expected_print_status(self):
        pass

if __name__ == '__main__':
    unittest.main()
