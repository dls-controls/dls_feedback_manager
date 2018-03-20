import sys
import os

from pkg_resources import require
require('cothread==2.13')
require('numpy==1.11.1')
require('epicsdbbuilder==1.0')

from softioc import softioc, builder


import myxbpmPVs
import myxbpmScripts


# Create the identity PVs
builder.SetDeviceName(myxbpmPVs.IOC_NAME % 'IOC')
builder.stringIn('WHOAMI', VAL = 'XBPM feedback controller')
builder.stringIn('HOSTNAME', VAL = os.uname()[1])

builder.LoadDatabase()
softioc.iocInit()

# Fire off the monitoring scripts:
myxbpmScripts.setup_fb_auto_onoff_pv()
myxbpmScripts.start_camonitors()


softioc.interactive_ioc(globals())
sys.exit()
