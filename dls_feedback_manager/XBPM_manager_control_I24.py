import sys
from pkg_resources import require
import logging

require('dls_feedback_manager==1.2')
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from softioc import softioc, builder

formatter = '%(asctime)s, %(funcName)s, %(levelname)s, %(message)s'
logging.basicConfig(format=formatter, level=logging.INFO)

## Creates name for feedback PVs created during run.
builder.SetDeviceName('BL24I-EA-FDBK-01')

import XBPM_range_manager, XBPM_feedback_manager, XBPM_pid_params

xbpm1_pid_params_list = [XBPM_pid_params.XBPMPIDParamsClass(
    KP=-0.0050,
    KI=0.000,
    KD=0.000,
    feedback="FPITCH:FB1",
    position="FB1"),  # pitch
                        XBPM_pid_params.XBPMPIDParamsClass(
    KP=-0.0100,
    KI=0.000,
    KD=0.000,
    feedback="FPITCH:FB2",
    position="FB2")]  # roll


## PVs shared by both XBPM1 and XBPM2 classes, assigns beamline number.
shared_PVs = XBPM_feedback_manager.XBPMSharedPVs(builder, '24')

## Run XBPM range manager
#  Input PV prefix, XBPM number, lower and upper current limits, TetrAMM scale
#  factor, position threshold percentage and ID energy gap PV name.
XBPM1 = XBPM_range_manager.XBPMRangeManager(
    builder,
    shared_PVs,
    tetramm_prefix='BL24I-EA-XBPM-',
    xbpm_num='01',
    lower_current_limit=50e-9,
    upper_current_limit=100e-9,
    optics=1.0,  # Leave as 1 unless FSWT featured in BL
    threshold_percentage=3.0,
    id_energy='')


## Run XBPM feedback manager
XBPM1_fdbk = XBPM_feedback_manager.XBPM1Feedback(
    builder,
    shared_PVs,
    xbpm1_pid_params_list,
    epics_fb_prefix1='BL24I-OP-DCM-01',
    xbpm1_num='01',
    mode_range1=(0, 1))
XBPM1_fdbk.make_on_startup()


builder.LoadDatabase()
softioc.iocInit()
softioc.interactive_ioc(globals())
sys.exit()
