from pkg_resources import require
require('cothread==2.13')
require('numpy==1.11.1')
require('epicsdbbuilder==1.0')

from softioc import builder

from epicsdbbuilder import records, MS, CP, ImportRecord

def Monitor(pv):
    return MS(CP(pv))

class XBPM_manager:

    def __init__(self, XBPM_prefix = 'BL04I-EA-XBPM-',XBPM_num = 0):
        self.XBPM_prefix = XBPM_prefix
        self.XBPM_num = XBPM_num

    def xbpm_vals(self, XBPM_prefix, XBPM_num):

        self.dx_mean_value = ImportRecord(XBPM_prefix + str(XBPM_num) + ':DiffX:MeanValue_RBV')
        self.sx_mean_value = ImportRecord(XBPM_prefix + str(XBPM_num) + ':SumX:MeanValue_RBV')
        self.dy_mean_value = ImportRecord(XBPM_prefix + str(XBPM_num) + ':DiffY:MeanValue_RBV')
        self.sy_mean_value = ImportRecord(XBPM_prefix + str(XBPM_num) + ':SumY:MeanValue_RBV')
        self.xbpm_sum_mean_value = ImportRecord(XBPM_prefix + str(XBPM_num) + ':SumAll:MeanValue_RBV')
        self.xbpm_x_beamsize = ImportRecord(XBPM_prefix + str(XBPM_num) + ':DRV:PositionScaleX')
        self.xbpm_y_beamsize = ImportRecord(XBPM_prefix + str(XBPM_num)+':DRV:PositionScaleY')

    def normal(self):

        self.xbpm_normx = records.calc('XBPM'+str(XBPM_num)+'_NORMX', CALC='A/B',
                               INPA = Monitor(self.dx_mean_value),
                               INPB = Monitor(self.sx_mean_value),
                               LOPR = -1,
                               HOPR = 1,
                               PINI = 'YES',
                               EGU = '')
        self.xbpm_normy = records.calc('XBPM'+str(XBPM_num)+'_NORMY', CALC='A/B',
                               INPA = Monitor(self.dy_mean_value),
                               INPB = Monitor(self.sy_mean_value),
                               LOPR = -1,
                               HOPR = 1,
                               PINI = 'YES',
                               EGU = '')

    def position_scale(self):
        self.fb_pid_scale = builder.aIn('FB_PID_SCALE',
                              initial_value = 1,
                              LOPR = 0,
                              HOPR = 1,
                              PINI = 'YES')
#class that inherits from
#class for FDBK1 and FDBK2


XBPM1 = XBPM_manager('BL04I-EA-XBPM-', 01)
XBPM2 = XBPM_manager('BL04I-EA-XBPM-', 02)

list_of_XBPMs = [XBPM1, XBPM2]

#for i in list_of_XBPMs:
#i.xbpm_vals()


##################
### CREATE PVS ###
##################


IOC_NAME = 'test:BL04I-EA-%s-01'

builder.SetDeviceName(IOC_NAME % 'FDBK')


# XBPM1 PID parameters
KPx1 = -1.800e-4
KIx1 = 1.250
KDx1 = 0.000
KPy1 = 1.0e-5 # NOTE: CHANGED ON 10/01/18 TO DEAL WITH TEMPORARY MOTOR ISSUE - SEE ELOG; KPy1 = 3.645e-5
KIy1 = 1.1042
KDy1 = 0.000

# XBPM2 PID parameters
KPx2 = -9.450e-5
KPx2 = -5.670e-5
KIx2 = 2.791
KDx2 = 0.0
KPy2 = 1.800e-4
KPy2 = 1.080e-4
KIy2 = 3.636
KDy2 = 0.0

kpx1 = builder.aIn('KPX1',
            initial_value = KPx1,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kix1 = builder.aIn('KIX1',
            initial_value = KIx1,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kdx1 = builder.aIn('KDX1',
            initial_value = KDx1,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kpy1 = builder.aIn('KPY1',
            initial_value = KPy1,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kiy1 = builder.aIn('KIY1',
            initial_value = KIy1,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kdy1 = builder.aIn('KDY1',
            initial_value = KDy1,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
            
kpx2 = builder.aIn('KPX2',
            initial_value = KPx2,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kix2 = builder.aIn('KIX2',
            initial_value = KIx2,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kdx2 = builder.aIn('KDX2',
            initial_value = KDx2,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kpy2 = builder.aIn('KPY2',
            initial_value = KPy2,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kiy2 = builder.aIn('KIY2',
            initial_value = KIy2,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
kdy2 = builder.aIn('KDY2',
            initial_value = KDy2,
            LOPR = 0, HOPR = 10.0, PINI = 'YES')
            



max_goodval = builder.aIn('MAX_GOODVAL',
            initial_value = 0.8,
            LOPR = 0,
            HOPR = 1.0,
            PINI = 'YES')
                 
goodx = builder.aIn('GOODX',
            initial_value = 1,
            LOPR = 0,
            HOPR = 1.0,
            PINI = 'YES')

goody = builder.aIn('GOODY',
            initial_value = 1,
            LOPR = 0,
            HOPR = 1.0,
            PINI = 'YES')

good = records.calc('GOOD', CALC='A*B',
            INPA = Monitor(goodx),
            INPB = Monitor(goody),
            LOPR = 0,
            HOPR = 1,
            PINI = 'YES',
            EGU = '') 


# Feedback status PV (acts as ON/OFF button for IOC).            
fb_enable_status = builder.mbbOut('FB_ENABLE',
            initial_value = 0,
            PINI = 'YES',
            NOBT = 2,
            ZRVL = 0,   ZRST = 'Stopped',
            ONVL = 1,   ONST = 'Run')


# Feedback status PV (acts as PAUSE for feedback).
fb_pause_status = builder.mbbOut('FB_PAUSE',
            initial_value = 1,
            PINI = 'YES',
            NOBT = 2,
            ZRVL = 0,   ZRST = 'Paused',
            ONVL = 1,   ONST = 'Ok to Run')


# Feedback mode PV, acts as button for the different modes (XBPM1, XBPM2)
fb_mode_status = builder.mbbOut('FB_MODE',
            initial_value = 1,
            PINI = 'YES',
            NOBT = 2,
            ZRVL = 0,   ZRST = 'Running on XBPM1',
            ONVL = 1,   ONST = 'Running on XBPM1 AND 2')


# Feedback FWST mode PV, acts as button for the different actuators (UPSTREAM, DOWNSTREAM)
fb_fswt_output = builder.mbbOut('FB_FSWTOUTPUT',
            initial_value = 1,
            PINI = 'YES',
            NOBT = 2,
            ZRVL = 0,   ZRST = 'Upstream actuator',
            ONVL = 1,   ONST = 'Downstream actuator')

fb_run1_status = builder.mbbOut('FB_RUN1',
            initial_value = 0,
            PINI = 'YES',
            NOBT = 2,
            ZRVL = 0,   ZRST = 'Stopped',
            ONVL = 1,   ONST = 'Run',
            TWVL = 2,   TWST = 'Paused')

fb_run2_status = builder.mbbOut('FB_RUN2',
            initial_value = 0,
            PINI = 'YES',
            NOBT = 2,
            ZRVL = 0,   ZRST = 'Stopped',
            ONVL = 1,   ONST = 'Run',
            TWVL = 2,   TWST = 'Paused')

# Limits for XBPM current and DCCT current.
minXCurr = builder.aIn('MIN_XBPMCURRENT',
            initial_value = 10e-9,
            LOPR = 0,
            HOPR = 1.0,
            PINI = 'YES')

minSRCurr = builder.aIn('MIN_DCCTCURRENT',
            initial_value = 8,
            LOPR = 0,
            HOPR = 310.0,
            PINI = 'YES')
            

# XBPM position builder
goodposx = builder.aIn('GOOD_POSX',
            initial_value = 0,
            LOPR = -1,
            HOPR = 1,
            PINI = 'YES')

goodposy = builder.aIn('GOOD_POSY',
            initial_value = 0,
            LOPR = -1,
            HOPR = 1,
            PINI = 'YES')


# XBPM position threshold PVs
threshold_percentage_xbpm1 = builder.aOut('THRESHOLDPC_XBPM1',
            initial_value = 3,
            LOPR = 0,
            HOPR = 100,
            PINI = 'YES')

threshold_percentage_xbpm2 = builder.aOut('THRESHOLDPC_XBPM2',
            initial_value = 3,
            LOPR = 0,
            HOPR = 100,
            PINI = 'YES')
            
position_threshold_ok_xbpm1 = records.calc('XBPM1POSITION_OK', CALC='(ABS(B)<(A/100)) && (ABS(C)<(A/100))',
            INPA = Monitor(threshold_percentage_xbpm1),
            INPB = Monitor(xbpm1_normx),
            INPC = Monitor(xbpm1_normy),
            LOPR = 0,
            HOPR = 1,
            PINI = 'YES',
            EGU = '')
            
position_threshold_ok_xbpm2 = records.calc('XBPM2POSITION_OK', CALC='(ABS(B)<(A/100)) && (ABS(C)<(A/100))',
            INPA = Monitor(threshold_percentage_xbpm2),
            INPB = Monitor(xbpm2_normx),
            INPC = Monitor(xbpm2_normy),
            LOPR = 0,
            HOPR = 1,
            PINI = 'YES',
            EGU = '') 

            


# XBPM signal chain check PVs
xbpm1SignalsOk = records.calc('XBPM1SIGNALS_OK', CALC='A>B',
            INPA = Monitor(xbpm1_sum_mean_value),
            INPB = Monitor(minXCurr),
            LOPR = 0,
            HOPR = 1,
            PINI = 'YES',
            EGU = '') 
            
xbpm2SignalsOk = records.calc('XBPM2SIGNALS_OK', CALC='A>B',
            INPA = Monitor(xbpm2_sum_mean_value),
            INPB = Monitor(minXCurr),
            LOPR = 0,
            HOPR = 1,
            PINI = 'YES',
            EGU = '') 
