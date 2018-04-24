import sys
import os

from pkg_resources import require
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from softioc import softioc, builder

builder.SetDeviceName('test:BL04I-EA-FDBK-01')

import XBPM_range_manager
import XBPM_feedback_manager


# Run XBPM range manager
#XBPM1 = XBPM_range_manager.RangeManager('test:BL04I-EA-XBPM-', '01', 90e-9, 110e-9, 1.0, 3.0, 'test:BL04I-MO-DCM-01:ENERGY')
#XBPM2 = XBPM_range_manager.RangeManager('test:BL04I-EA-XBPM-', '02', 90e-9, 110e-9, 1.0, 3.0, '')



# Run XBPM feedback manager
shared_PVs = XBPM_feedback_manager.XBPMSharedPVs('04')
XBPM1_fdbk = XBPM_feedback_manager.XBPM1_feedback(shared_PVs, 'test:BL04I-MO-DCM-01')
XBPM2_fdbk = XBPM_feedback_manager.XBPM2_feedback(shared_PVs, 'test:BL04I-MO-FSWT-01', 'test:BL04I-MO-DCM-01') # This needs fixing


builder.LoadDatabase()
softioc.iocInit()
softioc.interactive_ioc(globals())
sys.exit()
