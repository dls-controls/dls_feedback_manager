import sys
import os

from pkg_resources import require
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

import unittest

import test_range_manager
test_range = test_range_manager.RangeTests()

import test_feedback_manager

XBPMTestSuite = unittest.TestSuite()

def suite():
    tests = ['setUp,', 'test_standard_naming', 'test_regular_expression',
          'test_initial_variable_inputs', 'test_invalid_threshold_percentage', 'tearDown']

    return unittest.TestSuite(map(test_range, tests))

#  Run tests for XBPM range manager




# Run tests for XBPM feedback manager

test_feedback = test_feedback_manager.FeedbackTests()

