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
xbpm1_pid_params = [{"KPy1": -4.00e-5, "KIy1": 0.830, "KDy1": 0.000, "prefix": "FDBK1"},
                    {"KPx1": 1.80e-5, "KIx1": 0.830, "KDx1": 0.000, "prefix": "FDBK2"}]
xbpm2_pid_params = [{"KPy2": -4.00e-5, "KIy2": 0.830, "KDy2": 0.000, "prefix": "FDBK3"},
                    {"KPx2": 1.80e-5, "KIx2": 0.830, "KDx2": 0.000, "prefix": "FDBK4"}]


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
shared_PVs = XBPM_feedback_manager.XBPMSharedPVs('03')

## Run XBPM range manager
#  Input PV prefix, XBPM number, lower and upper current limits, TetrAMM scale factor, position threshold percentage and
#  ID energy gap PV name.
XBPM1 = XBPM_range_manager.XBPMRangeManager(shared_PVs, pv_prefix='test:BL03I-EA-XBPM-', xbpm_num='01',
                                            lower_current_limit=90e-9, upper_current_limit=110e-9,
                                            scale_factor=1.0, threshold_percentage=3.0,
                                            id_energy='test:BL03I-MO-DCM-01:ENERGY')
XBPM2 = XBPM_range_manager.XBPMRangeManager(shared_PVs, pv_prefix='test:BL03I-EA-XBPM-', xbpm_num='02',
                                            lower_current_limit=90e-9, upper_current_limit=110e-9,
                                            scale_factor=1.0, threshold_percentage=3.0, id_energy='')


## Run XBPM feedback manager
XBPM1_fdbk = XBPM_feedback_manager.XBPM1_feedback(shared_PVs, 'test:BL03I-MO-DCM-01', xbpm1_pid_params)
XBPM1_fdbk.make_on_startup()
XBPM2_fdbk = XBPM_feedback_manager.XBPM2_feedback(shared_PVs, 'test:BL03I-MO-DCM-01', 'test:BL03I-MO-DCM-01',  # fix
                                                  xbpm2_pid_params)
XBPM2_fdbk.make_on_startup()


builder.LoadDatabase()
softioc.iocInit()
softioc.interactive_ioc(globals())
sys.exit()
