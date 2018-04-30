import sys
from pkg_resources import require

require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from softioc import softioc, builder

builder.SetDeviceName('test:BL04I-EA-FDBK-01')

import XBPM_range_manager
import XBPM_feedback_manager


## XBPM1 and XBPM2 PID parameters (DCM and FSWT)
xbpm_pid_params = {"KPx1": -1.800e-4, "KIx1": 1.250,  "KDx1": 0.000,
                   "KPy1": 1.0e-5,    "KIy1": 1.1042, "KDy1": 0.000,
                   "KPx2": -5.670e-5, "KIx2": 2.791,  "KDx2": 0.0,
                   "KPy2": 1.080e-4,  "KIy2": 3.636,  "KDy2": 0.0}


## Shared PVs.
#  Gets called and constructed in the feedback manager to set up PVs shared by both XBPM1 and XBPM2 feedback classes.
#  Also gets used in the range manager to create the minimum current PVs.
#  It contains one argument, the beamline number (to be given as a string).
#  This gets inserted into the feedback manager to avoid being repetitively set throughout the file.
shared_PVs = XBPM_feedback_manager.XBPMSharedPVs('04', xbpm_pid_params)

## Run XBPM range manager
#  Input PV prefix, XBPM number, lower and upper current limits, TetrAMM scale factor, position threshold percentage and
#  ID energy gap PV name.
XBPM1 = XBPM_range_manager.XBPMRangeManager(shared_PVs, pv_prefix='test:BL04I-EA-XBPM-', xbpm_num='01', lower_current_limit=90e-9, upper_current_limit=110e-9, 1.0, 3.0,
                                            'test:BL04I-MO-DCM-01:ENERGY')
XBPM2 = XBPM_range_manager.XBPMRangeManager(shared_PVs, 'test:BL04I-EA-XBPM-', '02', 90e-9, 110e-9, 1.0, 3.0, '')


## Run XBPM feedback manager
XBPM1_fdbk = XBPM_feedback_manager.XBPM1_feedback(shared_PVs, 'test:BL04I-MO-DCM-01')
XBPM1_fdbk.make_on_startup()
XBPM2_fdbk = XBPM_feedback_manager.XBPM2_feedback(shared_PVs, 'test:BL04I-MO-FSWT-01', 'test:BL04I-MO-DCM-01')  # fix
XBPM2_fdbk.make_on_startup()


builder.LoadDatabase()
softioc.iocInit()
softioc.interactive_ioc(globals())
sys.exit()
