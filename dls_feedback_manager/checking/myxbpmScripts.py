import sys
import os
import time
import traceback

import cothread
from cothread import catools

if 'D' in sys.argv:
    def my_caput(pv, value, **args):
        print 'caput', pv, value, args
    catools.caput = my_caput

import myxbpmPVs

caput_listR1 = ['BL04I-MO-DCM-01:FDBK1:AUTOCALC.INPB','BL04I-MO-DCM-01:FDBK2:AUTOCALC.INPB',
                'BL04I-MO-DCM-01:FDBK1:AUTOCALC.INPC','BL04I-MO-DCM-01:FDBK2:AUTOCALC.INPC']
caput_listR2 = ['BL04I-MO-FSWT-01:FDBK1:AUTOCALC.INPB','BL04I-MO-FSWT-01:FDBK2:AUTOCALC.INPB',
                'BL04I-MO-FSWT-01:FDBK1:AUTOCALC.INPC','BL04I-MO-FSWT-01:FDBK2:AUTOCALC.INPC',
                'BL04I-MO-FSWT-01:FDBK3:AUTOCALC.INPB','BL04I-MO-FSWT-01:FDBK4:AUTOCALC.INPB',
                'BL04I-MO-FSWT-01:FDBK3:AUTOCALC.INPC','BL04I-MO-FSWT-01:FDBK4:AUTOCALC.INPC']

# Set up the Feedback AUTO ON/OFF PV names
def setup_fb_auto_onoff_pv():
    catools.caput(caput_listR1, myxbpmPVs.fb_run1_status.name + ' CP')

    catools.caput(caput_listR2, myxbpmPVs.fb_run2_status.name + ' CP')

camon_listFB = [myxbpmPVs.fb_enable_status.name, myxbpmPVs.fb_pause_status.name,
                myxbpmPVs.fb_fswt_output.name,'test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV',
                'test:SR-DI-DCCT-01:SIGNAL', 'test:FE04I-PS-SHTR-02:STA','test:BL04I-PS-SHTR-01:STA',
                'test:BL04I-EA-XBPM-02:SumAll:MeanValue_RBV','test:BL04I-TS-XBPM-01:FB_RUN1']

def start_camonitors():
    # Run monitor on the overall ON OFF button.
    #catools.camonitor(myxbpmPVs.fb_enable_status.name, checkFeedbackInputs)
    
    # Run monitor on the GDA PAUSE button.
    #catools.camonitor(myxbpmPVs.fb_pause_status.name, checkFeedbackInputs)
    
    # Run monitor on the FSWT feedback output button.
    #catools.camonitor(myxbpmPVs.fb_fswt_output.name, checkFeedbackInputs)
    
    # Run continuous checks for XBPM1 (RUN1) and XBPM2 (RUN2)
    # XBPM1 feedback checks (RUN1):
    catools.camonitor(camon_listFB, checkFeedbackInputs) # check XBPM signal currents
    
    # Range?
    catools.camonitor('test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV', checkRange1 ) # check XBPM signal currents
    catools.camonitor('test:BL04I-EA-XBPM-02:SumAll:MeanValue_RBV', checkRange2 ) # check XBPM signal currents
    
    # Run monitor on the ID gap. XBPM1; change scale factors if ID energy changes.
    catools.camonitor('test:BL04I-MO-DCM-01:ENERGY', setVerticalXBPM1ScaleFactor)
    catools.camonitor('test:BL04I-MO-DCM-01:ENERGY', setVerticalXBPM2ScaleFactor)
    
    # if NORMX,Y falls outside of good range...
    catools.camonitor(myxbpmPVs.good.name, setFeedbackPID )
    # set GOOD based on NORM value for X and Y..
    catools.camonitor(myxbpmPVs.xbpm1_normx.name, lambda x, a='X': normGood(x, a) )
    catools.camonitor(myxbpmPVs.xbpm1_normy.name, lambda x, a='Y': normGood(x, a) )
    
    
    

def checkRange1(val):
    r = catools.caget('test:BL04I-EA-XBPM-01:DRV:Range')
    if r == 0: # 120uA
        if val < 50e-9:
            catools.caput('BL04I-EA-XBPM-01:DRV:Range', 1)
            print(r, "r is 0")
    elif r == 1: # 120nA
        if val > 100e-9:
            catools.caput('BL04I-EA-XBPM-01:DRV:Range', 0)
            print(val, "r is 1")
    else:
        print(r, "r is not 0 or 1")

def checkRange2(val):
    r = catools.caget('test:BL04I-EA-XBPM-02:DRV:Range')
    if r == 0: # 120uA
        if val < 90e-9:
            catools.caput('BL04I-EA-XBPM-02:DRV:Range', 1)
            print(r, "r is 0")
    elif r == 1: # 120nA
        if val > 110e-9:
            catools.caput('BL04I-EA-XBPM-02:DRV:Range', 0)
            print(r, "r is 1")
    else:
        print(r, "r is not 0 or 1")



# STOP feedback if requested
def setRunStopped1():
    myxbpmPVs.fb_run1_status.set(0)

def setRunStopped2():
    myxbpmPVs.fb_run2_status.set(0)


# START (or restart) feedback if requested
def setRunStart1():
    myxbpmPVs.fb_run1_status.set(1)

def setRunStart2():
    myxbpmPVs.fb_run2_status.set(1)


# PAUSE feedback if requested 
def setRunPaused1():
    myxbpmPVs.fb_run1_status.set(2)

def setRunPaused2():
    myxbpmPVs.fb_run2_status.set(2)


def printfunction(printstatus, index):
    if index not in range(len(camon_listFB)):
        print(printstatus)
    else:
        print(printstatus, camon_listFB[index], index)

# What to do if any PVs change?
def checkFeedbackInputs(value, index=-1):
    if (
            catools.caget('test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV') > myxbpmPVs.minXCurr.get() and
            catools.caget('test:SR-DI-DCCT-01:SIGNAL') > myxbpmPVs.minSRCurr.get() and
            catools.caget('test:FE04I-PS-SHTR-02:STA') == 1 and
            catools.caget('test:BL04I-PS-SHTR-01:STA') == 1 and
            myxbpmPVs.fb_enable_status.get() == 1 and
            myxbpmPVs.fb_pause_status.get() == 1
        ):
        setRunStart1()
        printfunction("run1 started", index)
    elif myxbpmPVs.fb_pause_status.get() == 0:
        setRunPaused1()
        printfunction("run1 paused", index)
    else:
        setRunStopped1()
        printfunction("run1 stopped", index)
    
    if (
            catools.caget('test:BL04I-EA-XBPM-02:SumAll:MeanValue_RBV') > myxbpmPVs.minXCurr.get() and
            myxbpmPVs.fb_run1_status.get() == 1 and
            myxbpmPVs.fb_mode_status.get() == 1
        ):
        setRunStart2()
        print("run2 start",camon_listFB[index], index)
    elif myxbpmPVs.fb_pause_status.get() == 0:
        setRunPaused2()
        print("run2 paused",camon_listFB[index], index)
    else:
        setRunStopped2()
        print("run2 stopped",camon_listFB[index], index)


# Check the status of the ENABLE button for feedback. Set feedback on or off
# as is appropriate.
def checkEnableStatus(val):
    if val == 0:
        print "Feedback ENABLE button set to OFF (Stopped)"
        setRunStopped1()
        setRunStopped2()
    elif val == 1:
        print "Feedback ENABLE button set to ON (Running)"
        if myxbpmPVs.fb_mode_status == 0:
            print "  Feedback mode is XBPM1 operation only"
            setRunStart1()
            setRunStopped2()
        elif myxbpmPVs.fb_mode_status == 1:
            print "  Feedback mode is XBPM1 and XBPM2 operation"
            setRunStart1()
            setRunStart2()


# Set the vertical XBPM1 scale factor [um] based on the DCM energy [keV]
# This maths is based on the beam size calculation from the I04 undulator. For
# more information please see TDI-DIA-XBPM-REP-003.
def setVerticalXBPM1ScaleFactor(energy):
    ky = -26*energy + 1120
    kx = 1200
    catools.caput('BL04I-EA-XBPM-01:DRV:PositionScaleY', ky)
    catools.caput('BL04I-EA-XBPM-01:DRV:PositionScaleX', kx)
    
# Set the vertical XBPM2 scale factor [um] based on the DCM energy [keV]
# This is the same as XBPM1, but divided by 3.2
def setVerticalXBPM2ScaleFactor(energy):
    ky = (-26*energy + 1120) / 3.2
    kx = 1200/3.2
    catools.caput('BL04I-EA-XBPM-02:DRV:PositionScaleY', ky)
    catools.caput('BL04I-EA-XBPM-02:DRV:PositionScaleX', kx)

# Set feedback PID values, and a scale if wanted.
def setFeedbackPID(good):
    if good==1:
        scale = 1
    elif good!=1:
        scale = myxbpmPVs.fb_pid_scale.get()
    # Y DCM PITCH
    catools.caput('BL04I-MO-DCM-01:FDBK1.KP', scale*myxbpmPVs.kpy1.get() )
    catools.caput('BL04I-MO-DCM-01:FDBK1.KI', scale*myxbpmPVs.kiy1.get() )
    catools.caput('BL04I-MO-DCM-01:FDBK1.KD', scale*myxbpmPVs.kdy1.get() )
    # X DCM ROLL
    catools.caput('BL04I-MO-DCM-01:FDBK2.KP', scale*myxbpmPVs.kpx1.get() )
    catools.caput('BL04I-MO-DCM-01:FDBK2.KI', scale*myxbpmPVs.kix1.get() )
    catools.caput('BL04I-MO-DCM-01:FDBK2.KD', scale*myxbpmPVs.kdx1.get() )
    
    # X FSWT DOWNSTREAM
    catools.caput('BL04I-MO-FSWT-01:FDBK1.KP', scale*myxbpmPVs.kpx2.get() )
    catools.caput('BL04I-MO-FSWT-01:FDBK1.KI', scale*myxbpmPVs.kix2.get() )
    catools.caput('BL04I-MO-FSWT-01:FDBK1.KD', scale*myxbpmPVs.kdx2.get() )
    # Y FSWT DOWNSTREAM
    catools.caput('BL04I-MO-FSWT-01:FDBK2.KP', scale*myxbpmPVs.kpy2.get() )
    catools.caput('BL04I-MO-FSWT-01:FDBK2.KI', scale*myxbpmPVs.kiy2.get() )
    catools.caput('BL04I-MO-FSWT-01:FDBK2.KD', scale*myxbpmPVs.kdy2.get() )
    # X FSWT UPSTREAM
    catools.caput('BL04I-MO-FSWT-01:FDBK3.KP', scale*myxbpmPVs.kpx2.get() )
    catools.caput('BL04I-MO-FSWT-01:FDBK3.KI', scale*myxbpmPVs.kix2.get() )
    catools.caput('BL04I-MO-FSWT-01:FDBK3.KD', scale*myxbpmPVs.kdx2.get() )
    # Y FSWT UPSTREAM
    catools.caput('BL04I-MO-FSWT-01:FDBK4.KP', scale*myxbpmPVs.kpy2.get() )
    catools.caput('BL04I-MO-FSWT-01:FDBK4.KI', scale*myxbpmPVs.kiy2.get() )
    catools.caput('BL04I-MO-FSWT-01:FDBK4.KD', scale*myxbpmPVs.kdy2.get() )


# Check and set "normalised" values.
def normGood(val, a):
    max_goodval = myxbpmPVs.max_goodval.get()
    pv_name = myxbpmPVs.good.name
    if abs(val) > max_goodval:
        catools.caput('%s%s' % (pv_name, a), 0)
    elif abs(val) <= max_goodval:
        catools.caput('%s%s' % (pv_name, a), 1)
