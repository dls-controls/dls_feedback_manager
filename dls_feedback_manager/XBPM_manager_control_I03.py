import sys
from pkg_resources import require

require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from softioc import softioc, builder

builder.SetDeviceName('test:BL03I-EA-FDBK-01')

import XBPM_range_manager
import XBPM_feedback_manager


## XBPM1 and XBPM2 PID parameters (mirrors)
#  Initial values used in feedback manager
xbpm_pid_params = {"KPx1": 1.80e-5,  "KIx1": 0.830, "KDx1": 0.000,
                   "KPy1": -4.00e-5, "KIy1": 0.830, "KDy1": 0.000,
                   "KPx2": 1.80e-5,  "KIx2": 0.830, "KDx2": 0.000,
                   "KPy2": -4.00e-5, "KIy2": 0.830, "KDy2": 0.000}


## XBPM2 PID parameters DCM
#KPx2 = 2.60e-5
#KIx2 = 0.83
#KDx2 = 0.000
#KPy2 = -3.20e-5
#KIy2 = 0.83
#KDy2 = 0.000


## Shared PVs.
#  Gets called and constructed in the feedback manager to set up PVs shared by both XBPM1 and XBPM2 feedback classes.
#  Also gets used in the range manager to create the minimum current PVs.
#  It contains one argument, the beamline number (to be given as a string).
#  This gets inserted into the feedback manager to avoid being repetitively set throughout the file.
shared_PVs = XBPM_feedback_manager.XBPMSharedPVs('03', xbpm_pid_params)

## Run XBPM range manager
#  Input PV prefix, XBPM number, lower and upper current limits, TetrAMM scale factor, position threshold percentage and
#  ID energy gap PV name.
XBPM1 = XBPM_range_manager.RangeManager(shared_PVs, 'test:BL03I-EA-XBPM-', '01', 90e-9, 110e-9, 1.0, 3.0,
                                        'test:BL03I-MO-DCM-01:ENERGY')
XBPM2 = XBPM_range_manager.RangeManager(shared_PVs, 'test:BL03I-EA-XBPM-', '02', 90e-9, 110e-9, 1.0, 3.0, '')


## Run XBPM feedback manager
#  For XBPM2, FSWT is for I04, change to -DCM-02 for I03
XBPM1_fdbk = XBPM_feedback_manager.XBPM1_feedback(shared_PVs, 'test:BL03I-MO-DCM-01')
XBPM1_fdbk.make_on_startup()
XBPM2_fdbk = XBPM_feedback_manager.XBPM2_feedback(shared_PVs, 'test:BL03I-MO-DCM-01', 'test:BL03I-MO-DCM-01')  # fix
XBPM2_fdbk.make_on_startup()


builder.LoadDatabase()
softioc.iocInit()
softioc.interactive_ioc(globals())
sys.exit()
