import sys
from pkg_resources import require
import logging

require('dls_feedback_manager==1.2')
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from softioc import softioc, builder

formatter = '%(asctime)s, %(funcName)s, %(levelname)s, %(message)s'
logging.basicConfig(format=formatter, level=logging.DEBUG)

builder.SetDeviceName('BL04I-EA-FDBK-01')

import XBPM_range_manager, XBPM_feedback_manager,\
    XBPM_pid_params

xbpm1_pid_params_list = [XBPM_pid_params.XBPMPIDParamsClass(KP=1.0e-5,
                                                            KI=1.1042,
                                                            KD=0.000,
                                                            feedback="FDBK1",
                                                            position="Y1"),
                         XBPM_pid_params.XBPMPIDParamsClass(KP=-1.800e-4,
                                                            KI=1.250,
                                                            KD=0.000,
                                                            feedback="FDBK2",
                                                            position="X1")]
xbpm2_pid_params_list = [XBPM_pid_params.XBPMPIDParamsClass(KP=1.800e-4,
                                                            KI=3.636,
                                                            KD=0.0,
                                                            feedback="FDBK3",
                                                            position="Y2"),
                         XBPM_pid_params.XBPMPIDParamsClass(KP=-9.450e-5,
                                                            KI=2.791,
                                                            KD=0.0,
                                                            feedback="FDBK4",
                                                            position="X2")]

## Shared PVs.
#  Gets called and constructed in the feedback manager to set up PVs shared by
#  both XBPM1 and XBPM2 feedback classes.
#  Also gets used in the range manager to create the minimum current PVs.

shared_PVs = XBPM_feedback_manager.XBPMSharedPVs('04')

## Run XBPM range manager
#  Input PV prefix, XBPM number, lower and upper current limits, TetrAMM scale
#  factor, position threshold percentage and ID energy gap PV name.
XBPM1 = XBPM_range_manager.XBPMRangeManager(shared_PVs, pv_prefix=
                                            'BL04I-EA-XBPM-', xbpm_num='01',
                                            lower_current_limit=90e-9,
                                            upper_current_limit=110e-9,
                                            scale_factor=1.0,
                                            threshold_percentage=3.0,
                                            id_energy='BL04I-MO-DCM-01:ENERGY')
XBPM2 = XBPM_range_manager.XBPMRangeManager(shared_PVs, pv_prefix=
                                            'BL04I-EA-XBPM-', xbpm_num='02',
                                            lower_current_limit=90e-9,
                                            upper_current_limit=110e-9,
                                            scale_factor=1.0,
                                            threshold_percentage=3.0,
                                            id_energy='')


## Run XBPM feedback manager
XBPM1_fdbk = XBPM_feedback_manager.XBPM1_Feedback(shared_PVs,
                                                  'BL04I-MO-DCM-01',
                                                  xbpm1_pid_params_list,
                                                  xbpm1_num='01',
                                                  mode_range1=(0, 1))
XBPM1_fdbk.make_on_startup()
XBPM2_fdbk = XBPM_feedback_manager.XBPM2_Feedback(shared_PVs,
                                                  'BL04I-MO-FSWT-01',
                                                  'BL04I-MO-DCM-01',
                                                  xbpm2_pid_params_list,
                                                  xbpm2_num='02',
                                                  mode_range2=(1, 2))
XBPM2_fdbk.make_on_startup()


builder.LoadDatabase()
softioc.iocInit()
softioc.interactive_ioc(globals())
sys.exit()
