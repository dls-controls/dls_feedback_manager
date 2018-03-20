import sys
import os

from pkg_resources import require
require('cothread==2.13')
require('numpy==1.11.1')
require('epicsdbbuilder==1.0')

from softioc import softioc, builder


"""#builder.SetDeviceName('IOC-TEST')
builder.SetDeviceName('SFX44126-PY-IOC-01')

kpx1 = builder.aOut('KPX1',
            initial_value = 1.0,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')

fb_enable_status = builder.mbbOut('FB_ENABLE',
            initial_value = 0,
            PINI = 'YES',
            NOBT = 2,
            ZRVL = 0,   ZRST = 'Stopped',
            ONVL = 1,   ONST = 'Run')

threshold_percentage_xbpm1 = builder.aOut('THRESHOLDPC_XBPM1',
            initial_value = 3,
            LOPR = 0,
            HOPR = 100,
            PINI = 'YES') """

builder.SetDeviceName('test')

#xbpm1
x1sigcurr = builder.aOut('BL04I-EA-XBPM-01:SumAll:MeanValue_RBV',
                        initial_value = 30e-09)
x1SRcurr = builder.aOut('SR-DI-DCCT-01:SIGNAL',
                        initial_value = 302.721)
x1FEss = builder.mbbOut('FE04I-PS-SHTR-02:STA',
                     initial_value = 1) # front end shutter status
x1BLss = builder.mbbOut('BL04I-PS-SHTR-01:STA',
                      initial_value = 1)
#xbpm2
x2sigcurr = builder.aOut('BL04I-EA-XBPM-02:SumAll:MeanValue_RBV',
                    initial_value = 1.02991e-06)
xstat = builder.mbbOut('BL04I-TS-XBPM-01:FB_RUN1',
                       initial_value = 0)

#ID gap
x1SF = builder.aOut('BL04I-MO-DCM-01:ENERGY',
                    initial_value = 12.658)

#drvrange
x1r = builder.mbbOut('BL04I-EA-XBPM-01:DRV:Range',
                      initial_value = 0)
x2r = builder.mbbOut('BL04I-EA-XBPM-02:DRV:Range',
                      initial_value = 0)

# Create the identity PVs

builder.stringIn('WHOAMI', VAL = 'XBPM feedback controller')
builder.stringIn('HOSTNAME', VAL = os.uname()[1])

builder.LoadDatabase()
softioc.iocInit()



softioc.interactive_ioc(globals())
sys.exit()