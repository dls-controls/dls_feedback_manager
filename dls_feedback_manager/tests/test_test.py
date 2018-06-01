#!/usr/bin/env dls-python

import unittest
from pkg_resources import require
require('mock')
from mock import Mock, MagicMock, patch
import XBPM_feedback_manager


#  Unittests for XBPM Feedback Manager.

class FeedbackTests(unittest.TestCase):

    @patch('builder.mbbOut')
    def test_create_pid_pvs_gets_called(self, MockXBPM2_feedback):
        pvs = MockXBPM2_feedback()
        pvs.create_pid_pvs.return_value = {"a": 5, "b": 10}

        response = pvs.create_pid_pvs()
        self.assertIsNotNone(response)
        self.assertIsInstance(response, dict)

        assert MockXBPM2_feedback is XBPM_feedback_manager.XBPM2Feedback
        assert MockXBPM2_feedback.called
        pvs.reset_mock()
        pvs.create_pid_pvs.assert_not_called()


if __name__ == "__main__":
    unittest.main()
