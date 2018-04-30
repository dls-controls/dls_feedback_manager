import sys
import os

from pkg_resources import require
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

import unittest

import test_range_manager
import test_feedback_manager
test_range = test_range_manager.RangeTests()
test_feedback = test_feedback_manager.FeedbackTests()

if __name__ == "__main__":
    unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=2).run('test*.py')


# XBPMTestSuite = unittest.TestSuite()

#def suite():
 #  tests = ['setUp,', 'test_standard_naming', 'test_regular_expression',

  #      'test_initial_variable_inputs', 'test_invalid_threshold_percentage', 'tearDown']

   #return unittest.TestSuite(map(test_range, tests))

#  Run tests for XBPM range manager

#if __name__ == "main":
 #   unittest.TestLoader().loadTestsFromModule(test_range_manager)
  #  unittest.TextTestRunner(verbosity=2).run('.')

#suite = unittest.TestLoader().loadTestsFromTestCase(test_range_manager.RangeTests)
#unittest.TextTestRunner(verbosity=2).run(suite)

# Run tests for XBPM feedback manager

