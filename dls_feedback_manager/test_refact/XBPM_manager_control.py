import sys
import os

from pkg_resources import require
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from softioc import softioc, builder

import XBPM_range_manager
import XBPM_feedback_manager

softioc.iocInit()


# Run XBPM range manager
XBPM1 = XBPM_range_manager.RangeManager('BL04I-EA-XBPM-', '01', 90e-9, 110e-9, 1.0, 3.0)
XBPM2 = XBPM_range_manager.RangeManager('BL04I-EA-XBPM-', '02', 90e-9, 110e-9, 3.2, 3.0)


# Run XBPM feedback manager
shared_PVs = XBPM_feedback_manager.XBPMSharedPVs()
DCM_fdbk = XBPM_feedback_manager.XBPM_DCMFeedback(shared_PVs)
FSWT_fdbk = XBPM_feedback_manager.XBPM_FSWTfeedback(shared_PVs)


softioc.interactive_ioc(globals())
sys.exit()
