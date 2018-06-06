import sys
import os

from pkg_resources import require
require('cothread==2.13')
require('numpy==1.11.1')
require('epicsdbbuilder==1.0')

from softioc import softioc, builder
from epicsdbbuilder import records #, MS, CP, ImportRecord

##############################################

builder.SetDeviceName('BL24I-EA-XBPM-01')

x1sigcurr = builder.aOut('SumAll:MeanValue_RBV', initial_value=5)
x1r = builder.mbbOut('DRV:Range', initial_value=0)
x1psy = builder.mbbOut('DRV:PositionScaleY', initial_value=1)
x1psx = builder.mbbOut('DRV:PositionScaleX', initial_value=1)


##############################################

builder.SetDeviceName('BL24I-OP-DCM-01')

A = 1
x1SF = builder.aOut('ENERGY', initial_value=11.882)
pitch = builder.aOut('FPITCH:FB1', initial_value=0.554)
roll = builder.aOut('FPITCH:FB2', initial_value=0.0261)


##############################################

builder.SetDeviceName('SR-DI-DCCT-01')

x1SRcurr = builder.aOut('SIGNAL', initial_value=10)

##############################################

builder.SetDeviceName('FE24I-PS-SHTR-02')

x1FEss = builder.mbbOut('STA', initial_value=1)  # front end shutter status

##############################################

builder.SetDeviceName('BL24I-PS-SHTR-01')

x1BLss = builder.mbbOut('STA',
                        initial_value=1)


# Create the identity PVs

builder.stringIn('WHOAMI', VAL='XBPM feedback controller')
builder.stringIn('HOSTNAME', VAL=os.uname()[1])

builder.LoadDatabase()
softioc.iocInit()


softioc.interactive_ioc(globals())
sys.exit()
