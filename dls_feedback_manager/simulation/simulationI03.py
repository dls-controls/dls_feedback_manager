import sys
import os

from pkg_resources import require
require('cothread==2.13')
require('numpy==1.11.1')
require('epicsdbbuilder==1.0')

from softioc import softioc, builder
from epicsdbbuilder import records #, MS, CP, ImportRecord


"""#builder.SetDeviceName('IOC-TEST')
builder.SetDeviceName('SFX44126-PY-IOC-01')
"""

builder.SetDeviceName('BL03I-EA-XBPM-01')

x1sigcurr = builder.aOut('SumAll:MeanValue_RBV', initial_value=30e-09)
x1r = builder.mbbOut('DRV:Range', initial_value=0)
x1psy = builder.mbbOut('DRV:PositionScaleY', initial_value=1)
x1psx = builder.mbbOut('DRV:PositionScaleX', initial_value=1)


builder.SetDeviceName('BL03I-EA-XBPM-02')

x2sigcurr = builder.aOut('SumAll:MeanValue_RBV', initial_value=1.02991e-06)
x2r = builder.mbbOut('DRV:Range', initial_value=0)
x2psy = builder.mbbOut('DRV:PositionScaleY', initial_value=1)
x2psx = builder.mbbOut('DRV:PositionScaleX', initial_value=1)


builder.SetDeviceName('BL03I-MO-DCM-01')

A = 1
x1SF = builder.aOut('ENERGY', initial_value=12.658)
rc1 = records.calc('FDBK1:AUTOCALC', CALC=A)
rc2 = records.calc('FDBK2:AUTOCALC', CALC=A)
rc5 = records.calc('FDBK3:AUTOCALC', CALC=A)
rc6 = records.calc('FDBK4:AUTOCALC', CALC=A)


builder.SetDeviceName('SR-DI-DCCT-01')

x1SRcurr = builder.aOut('SIGNAL', initial_value = 302.721)


builder.SetDeviceName('FE03I-PS-SHTR-02')

x1FEss = builder.mbbOut('STA', initial_value=1)  # front end shutter status


builder.SetDeviceName('BL03I-PS-SHTR-01')

x1BLss = builder.mbbOut('STA',
                      initial_value = 1)



# PID params
#fb1 = records.epid('BL03I-MO-DCM-01:FDBK1', initial_value=1)  # complaint about 'bad character'?


# Create the identity PVs

builder.stringIn('WHOAMI', VAL = 'XBPM feedback controller')
builder.stringIn('HOSTNAME', VAL = os.uname()[1])

builder.LoadDatabase()
softioc.iocInit()



softioc.interactive_ioc(globals())
sys.exit()
