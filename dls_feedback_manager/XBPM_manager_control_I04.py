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

## Creates name for feedback PVs created during run.
builder.SetDeviceName('BL04I-EA-FDBK-01')

import XBPM_range_manager, XBPM_feedback_manager, XBPM_pid_params

xbpm1_pid_params_list = [XBPM_pid_params.XBPMPIDParamsClass(
    KP=1.0e-5,
    KI=1.1042,
    KD=0.000,
    feedback="FDBK1",
    position="Y1"),
                        XBPM_pid_params.XBPMPIDParamsClass(
    KP=-1.800e-4,
    KI=1.250,
    KD=0.000,
    feedback="FDBK2",
    position="X1")]

xbpm2_pid_params_list = [XBPM_pid_params.XBPMPIDParamsClass(
    KP=1.080e-4,
    KI=3.636,
    KD=0.0,
    feedback="FDBK3",
    position="Y2"),
                        XBPM_pid_params.XBPMPIDParamsClass(
    KP=-5.670e-5,
    KI=2.791,
    KD=0.0,
    feedback="FDBK4",
    position="X2")]

## PVs shared by both XBPM1 and XBPM2 classes, assigns beamline number.
shared_PVs = XBPM_feedback_manager.XBPMSharedPVs('04')

## Run XBPM range manager
#  Input PV prefix, XBPM number, lower and upper current limits, TetrAMM scale
#  factor, position threshold percentage and ID energy gap PV name.
XBPM1 = XBPM_range_manager.XBPMRangeManager(
    shared_PVs,
    pv_prefix='BL04I-EA-XBPM-',
    xbpm_num='01',
    lower_current_limit=50e-9,
    upper_current_limit=100e-9,
    fswt_strength=1.0,
    threshold_percentage=3.0,
    id_energy='BL04I-MO-DCM-01:ENERGY')

XBPM2 = XBPM_range_manager.XBPMRangeManager(
    shared_PVs,
    pv_prefix='BL04I-EA-XBPM-',
    xbpm_num='02',
    lower_current_limit=90e-9,
    upper_current_limit=110e-9,
    fswt_strength=3.2,
    threshold_percentage=3.0,
    id_energy='BL04I-MO-DCM-01:ENERGY')


## Run XBPM feedback manager
XBPM1_fdbk = XBPM_feedback_manager.XBPM1Feedback(
    shared_PVs,
    xbpm1_pid_params_list,
    xbpm1_prefix='BL04I-MO-DCM-01',
    xbpm1_num='01',
    mode_range1=(0, 1))
XBPM1_fdbk.make_on_startup()

XBPM2_fdbk = XBPM_feedback_manager.XBPM2Feedback(
    shared_PVs,
    xbpm2_pid_params_list,
    xbpm2_prefix='BL04I-MO-FSWT-01',
    xbpm1_prefix='BL04I-MO-DCM-01',
    xbpm2_num='02',
    mode_range2=(1, 2))
XBPM2_fdbk.make_on_startup()


builder.LoadDatabase()
softioc.iocInit()
softioc.interactive_ioc(globals())
sys.exit()
