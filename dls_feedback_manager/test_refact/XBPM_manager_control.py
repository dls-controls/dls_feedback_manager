import sys
import os

from pkg_resources import require
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.0')

from softioc import softioc, builder

import XBPM_range_manager
import XBPM_feedback_manager
import test_range_manager
import test_feedback_manager

# Run XBPM range manager - see file for variable definitions

XBPM1 = XBPM_range_manager.range_manager('BL04I-EA-XBPM-', '01', 90e-9, 110e-9, 1.0, 3.0)
XBPM2 = XBPM_range_manager.range_manager('BL04I-EA-XBPM-', '02', 90e-9, 110e-9, 3.2, 3.0)

# Run unittests for range manager

test_range_manager.RangeTests()

# Run XBPM feedback manager

XBPM_feedback_manager.XBPM_DCMFeedback()
XBPM_feedback_manager.XBPM_FSWTfeedback()

# Make PVs and start monitors

XBPM_feedback_manager.XBPM_DCMFeedback.make_on_start_up()

# Run unittests for feedback manager

test_feedback_manager.FeedbackTests()

sys.exit()
