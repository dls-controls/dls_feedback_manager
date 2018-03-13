import sys
import os

from pkg_resources import require
require('cothread==2.13')
require('numpy==1.11.1')
require('epicsdbbuilder==1.0')

from softioc import softioc, builder


#builder.SetDeviceName('IOC-TEST')
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
            PINI = 'YES')


# Create the identity PVs

builder.stringIn('WHOAMI', VAL = 'XBPM feedback controller')
builder.stringIn('HOSTNAME', VAL = os.uname()[1])

builder.LoadDatabase()
softioc.iocInit()



softioc.interactive_ioc(globals())
sys.exit()