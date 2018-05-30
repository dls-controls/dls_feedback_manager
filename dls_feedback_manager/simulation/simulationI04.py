import sys
import os

from pkg_resources import require
require('cothread==2.13')
require('numpy==1.11.1')
require('epicsdbbuilder==1.0')

from softioc import softioc, builder
from epicsdbbuilder import records #, MS, CP, ImportRecord

##############################################

builder.SetDeviceName('BL04I-EA-XBPM-01')

x1sigcurr = builder.aOut('SumAll:MeanValue_RBV', initial_value=5)
x1r = builder.mbbOut('DRV:Range', initial_value=0)
x1psy = builder.mbbOut('DRV:PositionScaleY', initial_value=790)
x1psx = builder.mbbOut('DRV:PositionScaleX', initial_value=1200)

##############################################

builder.SetDeviceName('BL04I-EA-XBPM-02')

x2sigcurr = builder.aOut('SumAll:MeanValue_RBV', initial_value=7)
x2r = builder.aOut('DRV:Range', initial_value=0)
x2psy = builder.aOut('DRV:PositionScaleY', initial_value=247)
x2psx = builder.aOut('DRV:PositionScaleX', initial_value=1200)

##############################################

builder.SetDeviceName('BL04I-MO-DCM-01')

A = 1
x1SF = builder.aOut('ENERGY', initial_value=12.658)
rc1 = records.calc('FDBK1:AUTOCALC', CALC=A)
rc2 = records.calc('FDBK2:AUTOCALC', CALC=A)

##############################################

builder.SetDeviceName('BL04I-MO-FSWT-01')

A = 1
rc1f = records.calc('FDBK1:AUTOCALC', CALC=A)
rc2f = records.calc('FDBK2:AUTOCALC', CALC=A)
rc3 = records.calc('FDBK3:AUTOCALC', CALC=A)
rc4 = records.calc('FDBK4:AUTOCALC', CALC=A)

##############################################

builder.SetDeviceName('SR-DI-DCCT-01')

x1SRcurr = builder.aOut('SIGNAL', initial_value=10)

##############################################

builder.SetDeviceName('FE04I-PS-SHTR-02')

x1FEss = builder.mbbOut('STA', initial_value=1)  # front end shutter status

##############################################

builder.SetDeviceName('BL04I-PS-SHTR-01')

x1BLss = builder.mbbOut('STA',
                        initial_value=1)


# Create the identity PVs

builder.stringIn('WHOAMI', VAL='XBPM feedback controller')
builder.stringIn('HOSTNAME', VAL=os.uname()[1])

builder.LoadDatabase()
softioc.iocInit()


softioc.interactive_ioc(globals())
sys.exit()
