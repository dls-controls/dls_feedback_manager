import sys
from pkg_resources import require

require('dls_feedback_manager')
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from softioc import softioc, builder

builder.SetDeviceName('BL03I-EA-FDBK-01')

import XBPM_range_manager
import XBPM_feedback_manager


## XBPM1 and XBPM2 PID parameters (mirrors)
#  Initial values used in feedback manager
#  FDBK1 = Y1, FDBK2 = X1, FDBK3 = Y2, FDBK4 = X2 - MAYBE MAKE THIS INTO VARIABLES
#  TO USE FOR CREATE PID PARAMS
xbpm1_pid_params = [{"KP": -4.00e-5, "KI": 0.830, "KD": 0.000, "prefix": "FDBK1", "pos": "Y1"},
                    {"KP": 1.80e-5,  "KI": 0.830, "KD": 0.000, "prefix": "FDBK2", "pos": "X1"}]

xbpm2_pid_params = [{"KP": -4.00e-5, "KI": 0.830, "KD": 0.000, "prefix": "FDBK3", "pos": "Y2"},
                    {"KP": 1.80e-5,  "KI": 0.830, "KD": 0.000, "prefix": "FDBK4", "pos": "X2"}]


## Shared PVs.
#  Gets called and constructed in the feedback manager to set up PVs shared by both XBPM1 and XBPM2 feedback classes.
#  Also gets used in the range manager to create the minimum current PVs.
#  It contains one argument, the beamline number (to be given as a string).
#  This gets inserted into the feedback manager to avoid being repetitively set throughout the file.
shared_PVs = XBPM_feedback_manager.XBPMSharedPVs('03')

## Run XBPM range manager
#  Input PV prefix, XBPM number, lower and upper current limits, TetrAMM scale factor, position threshold percentage and
#  ID energy gap PV name.
XBPM1 = XBPM_range_manager.XBPMRangeManager(shared_PVs, pv_prefix='BL03I-EA-XBPM-', xbpm_num='01',
                                            lower_current_limit=90e-9, upper_current_limit=110e-9,
                                            scale_factor=1.0, threshold_percentage=3.0,
                                            id_energy='BL03I-MO-DCM-01:ENERGY')
XBPM2 = XBPM_range_manager.XBPMRangeManager(shared_PVs, pv_prefix='BL03I-EA-XBPM-', xbpm_num='02',
                                            lower_current_limit=90e-9, upper_current_limit=110e-9,
                                            scale_factor=1.0, threshold_percentage=3.0, id_energy='')


## Run XBPM feedback manager
XBPM1_fdbk = XBPM_feedback_manager.XBPM1_Feedback(shared_PVs, 'BL03I-MO-DCM-01', xbpm1_pid_params)
XBPM1_fdbk.make_on_startup()
XBPM2_fdbk = XBPM_feedback_manager.XBPM2_Feedback(shared_PVs, 'BL03I-MO-DCM-01', 'BL03I-MO-DCM-01',  # fix
                                                  xbpm2_pid_params)
XBPM2_fdbk.make_on_startup()


builder.LoadDatabase()
softioc.iocInit()
softioc.interactive_ioc(globals())
sys.exit()
