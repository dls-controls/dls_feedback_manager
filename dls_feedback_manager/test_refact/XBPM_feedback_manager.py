
from pkg_resources import require
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

import cothread
from cothread import catools
from softioc import builder
from epicsdbbuilder import records, MS, CP, ImportRecord

def Monitor(pv):
    return MS(CP(pv))

import unittest

## XBPM1 PID parameters
KPx1 = -1.800e-4
KIx1 = 1.250
KDx1 = 0.000
KPy1 = 1.0e-5 # NOTE: CHANGED ON 10/01/18 TO DEAL WITH TEMPORARY MOTOR ISSUE - SEE ELOG; KPy1 = 3.645e-5
KIy1 = 1.1042
KDy1 = 0.000

# XBPM2 PID parameters
KPx2 = -5.670e-5
KIx2 = 2.791
KDx2 = 0.0
KPy2 = 1.080e-4
KIy2 = 3.636
KDy2 = 0.0

## PVs used for both DCM and FSWT.
class XBPMSharedPVs:

    ## Constructor.
    def __init__(self):
        self.create_feedback_status_PV()
        self.create_xbpm_current()
        self.status_options = {0:'Stopped', 1:'Run', 2:'Paused'}
        # For running monitors on overall ON/OFF button, GDA PAUSE button
        self.button_monitor = [self.fb_enable_status.name, self.fb_pause_status.name]

    ##  Restricts caput to anything other than options given.
    def validate_status_options(self):
       assert self.status_options in [0, 1, 2]

    ## What to do if any PVs change.
    def create_feedback_status_PV(self):
        # Feedback status PV (acts as ON/OFF button for IOC).
        self.fb_enable_status = builder.mbbOut('FB_ENABLE',
                        initial_value = 0,
                        PINI = 'YES',
                        NOBT = 2,
                        ZRVL = 0,   ZRST = 'Stopped',
                        ONVL = 1,   ONST = 'Run')

        # Feedback status PV (acts as PAUSE for feedback).
        self.fb_pause_status = builder.mbbOut('FB_PAUSE',
                        initial_value = 1,
                        PINI = 'YES',
                        NOBT = 2,
                        ZRVL = 0,   ZRST = 'Paused',
                        ONVL = 1,   ONST = 'Ok to Run')

        ## Feedback mode PV, acts as button for the different modes (XBPM1, XBPM2).
        #  XBPM1 and XBPM2 can run independently or in tandem.
        self.fb_mode_status = builder.mbbOut('FB_MODE',
                                             initial_value=0,
                                             PINI='YES',
                                             NOBT=2,
                                             ZRVL=0, ZRST='Running on XBPM1',
                                             ONVL=1, ONST='Running on XBPM1 AND 2',
                                             TWVL=2, TWST='Running on XBPM2')


    ## Limits for XBPM current
    def create_xbpm_current(self):
        self.minXCurr = builder.aIn('MIN_XBPMCURRENT',
                                    initial_value=10e-9,
                                    LOPR=0,
                                    HOPR=1.0,
                                    PINI='YES')

        self.minSRCurr = builder.aIn('MIN_DCCTCURRENT',
                                     initial_value=8,
                                     LOPR=0,
                                     HOPR=310.0,
                                     PINI='YES')


## XBPM1 feedback
class XBPM1_feedback:

    ## Constructor.
    #  Sets the prefix for XBPM1.
    def __init__(self, XBPMSharedPVs, xbpm1_prefix):
        self.XBPMSharedPVs = XBPMSharedPVs
        self.prefix = xbpm1_prefix

        print(self.prefix + " constructor successful")

    def make_on_startup(self):
        self.create_PVs()
        self.create_PID_PVs()
        # For setting up the Feedback AUTO ON/OFF PV names
        self.caput_list = [self.prefix + ':FDBK1:AUTOCALC.INPB', self.prefix + ':FDBK2:AUTOCALC.INPB',
                           self.prefix + ':FDBK1:AUTOCALC.INPC', self.prefix + ':FDBK2:AUTOCALC.INPC']
        self.setup_names()
        # Run continuous checks for XBPM1
        self.xbpm_fbcheck = ['test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV',
                             'test:SR-DI-DCCT-01-SIGNAL',
                             'test:BL04I-PS-SHTR-01:STA']
        self.start_camonitors()

    ## Set up feedback auto on/off PV names
    def setup_names(self):
        catools.caput(self.caput_list, self.fb_run_status.name + ' CP')

    ## Sets run status to initial value
    def set_run_status(self, status):
        self.fb_run_status.set(self.XBPMSharedPVs.status_options[status])

    ## Get the current run status.
    def get_run_status(self):
        self.fb_run_status.get()


    ## Created in the constructor.
    #  Used in check_feedback_inputs to specify conditions for setting new status
    #  if the PVs for DCM change.
    def create_PVs(self):
        self.fb_run_status = builder.mbbOut('FB_RUN1',
                                       initial_value=0,
                                       PINI='YES',
                                       NOBT=2,
                                       ZRVL=0, ZRST='Stopped',
                                       ONVL=1, ONST='Run',
                                       TWVL=2, TWST='Paused')



    ## Created in constructor.
    #  Set limits for each PID parameter.
    def create_PID_PVs(self):
        self.kpx1 = builder.aIn('KPX1',
                           initial_value=KPx1,
                           LOPR=-500.0, HOPR=500.0, PINI='YES')
        self.kix1 = builder.aIn('KIX1',
                           initial_value=KIx1,
                           LOPR=-500, HOPR=500, PINI='YES')
        self.kdx1 = builder.aIn('KDX1',
                           initial_value=KDx1,
                           LOPR=-500, HOPR=500, PINI='YES')
        self.kpy1 = builder.aIn('KPY1',
                           initial_value=KPy1,
                           LOPR=-500, HOPR=500, PINI='YES')
        self.kiy1 = builder.aIn('KIY1',
                           initial_value=KIy1,
                           LOPR=-500, HOPR=500, PINI='YES')
        self.kdy1 = builder.aIn('KDY1',
                           initial_value=KDy1,
                           LOPR=-500, HOPR=500, PINI='YES')


    ## Monitor the feedback enable/pause buttons and checks the feedback input to set a new feedback status.
    def start_camonitors(self):
        catools.camonitor(self.XBPMSharedPVs.fb_enable_status.name, self.check_enable_status)
        catools.camonitor(self.XBPMSharedPVs.button_monitor, self.check_feedback_inputs)
        catools.camonitor(self.xbpm_fbcheck, self.check_feedback_inputs)


    ## Print the status.
    #  State which item in the list is being referred to.
    def print_function(self, printstatus):
        print(printstatus)


    ## Check the status of the ENABLE button for feedback.
    #  Set feedback on or off as is appropriate.
    def check_enable_status(self, val):
        if self.XBPMSharedPVs.fb_enable_status.get() == 0:
            print "Feedback ENABLE button set to OFF (Stopped)"
            self.set_run_status(0)
        elif self.XBPMSharedPVs.fb_enable_status.get() == 1:
            print "Feedback ENABLE button set to ON (Running)"
            if self.XBPMSharedPVs.fb_mode_status.get() == 0:
                print "Feedback mode is XBPM1 operation only"
                self.set_run_status(1)
            elif self.XBPMSharedPVs.fb_mode_status.get() == 1:
                print "Feedback mode is XBPM1 and XBPM2 operation"
                self.set_run_status(1)
            elif self.XBPMSharedPVs.fb_mode_status.get() == 2:
                print "Feedback mode is XBPM2 operation only"


    ## What to do if any PVs change.
    #  Define conditions for setting new status.
    def check_feedback_inputs(self, val, index):
        if (
            catools.caget('test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV') > self.XBPMSharedPVs.minXCurr.get() and
            catools.caget('test:SR-DI-DCCT-01:SIGNAL') > self.XBPMSharedPVs.minSRCurr.get() and
            catools.caget('test:FE04I-PS-SHTR-02:STA') == 1 and
            catools.caget('test:BL04I-PS-SHTR-01:STA') == 1 and
            self.XBPMSharedPVs.fb_enable_status.get() == 1 and
            self.XBPMSharedPVs.fb_pause_status.get() == 1 and
            self.XBPMSharedPVs.fb_mode_status.get() == 0
        ):
            self.set_run_status(1)
            self.print_function("Run for XBPM1 Started")
        elif self.XBPMSharedPVs.fb_pause_status.get() == 0:
            self.set_run_status(2)
            self.print_function("Run for XBPM1 Paused")
        else:
            self.set_run_status(0)
            self.print_function("Run for XBPM1 Stopped")



## XBPM2 feedback
class XBPM2_feedback(XBPM1_feedback):

    ## Constructor.
    #  Overrides prefix.
    #  Recreates feedback enable and pause buttons.
    def __init__(self, XBPMSharedPVs, xbpm2_prefix, xbpm1_prefix): # Solve prefix problem
        XBPM1_feedback.__init__(self, XBPMSharedPVs, xbpm1_prefix)
        self.XBPMSharedPVs = XBPMSharedPVs
        self.prefix = xbpm2_prefix

        print(self.prefix + " constructor successful")

    def make_on_startup(self):
        self.create_PVs()
        self.create_PID_PVs()

        # For setting up feedback AUTO ON/OFF PV names
        self.caput_list = [self.prefix + ':FDBK1:AUTOCALC.INPB', self.prefix + ':FDBK2:AUTOCALC.INPB',
                           self.prefix + ':FDBK1:AUTOCALC.INPC', self.prefix + ':FDBK2:AUTOCALC.INPC',
                           self.prefix + ':FDBK3:AUTOCALC.INPB', self.prefix + ':FDBK4:AUTOCALC.INPB',
                           self.prefix + ':FDBK3:AUTOCALC.INPC', self.prefix + ':FDBK4:AUTOCALC.INPC']
        self.setup_names()
        # Run continuous checks for XBPM2
        self.xbpm_fbcheck = ['FE04I-PS-SHTR-02:STA',
                             'BL04I-EA-XBPM-02:SumAll:MeanValue:RBV']
        self.start_camonitors()

    ## Created in the constructor.
    #  Used in check_feedback_inputs to specify conditions for setting new status
    #  if the PV for FSWT change.
    def create_PVs(self):
        self.fb_run_status = builder.mbbOut('FB_RUN2',
                                            initial_value=0,
                                            PINI='YES',
                                            NOBT=2,
                                            ZRVL=0, ZRST='Stopped',
                                            ONVL=1, ONST='Run',
                                            TWVL=2, TWST='Paused')


    ## Created in constructor.
    #  Set limits for each PID parameter.
    def create_PID_PVs(self):
        self.kpx2 = builder.aIn('KPX2',
                                initial_value=KPx2,
                                LOPR=-500.0, HOPR=500.0, PINI='YES')
        self.kix2 = builder.aIn('KIX2',
                                initial_value=KIx2,
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kdx2 = builder.aIn('KDX2',
                                initial_value=KDx2,
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kpy2 = builder.aIn('KPY2',
                                initial_value=KPy2,
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kiy2 = builder.aIn('KIY2',
                                initial_value=KIy2,
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kdy2 = builder.aIn('KDY2',
                                initial_value=KDy2,
                                LOPR=-500, HOPR=500, PINI='YES')


    # Check the status of the ENABLE button for feedback.
    # Set feedback on or off as is appropriate.
    def check_enable_status(self, val):
        if self.XBPMSharedPVs.fb_enable_status.get() == 0:
            print "Feedback ENABLE button set to OFF (Stopped)"
            self.set_run_status(0)
        elif self.XBPMSharedPVs.fb_enable_status.get() == 1:
            print "Feedback ENABLE button set to ON (Running)"
            if self.XBPMSharedPVs.fb_mode_status.get() == 0:
                print "Feedback mode is XBPM1 operation only"
                self.set_run_status(0)
            elif self.XBPMSharedPVs.fb_mode_status.get() == 1:
                print "Feedback mode is XBPM1 and XBPM2 operation"
                self.set_run_status(1)
            elif self.XBPMSharedPVs.fb_mode_status.get() == 2:
                print "Feedback mode is XBPM2 operation"
                self.set_run_status(1)


    ## What to do if any PVs change.
    #  Define conditions for setting new status.
    def check_feedback_inputs(self, val, index):
        if (catools.caget('test:BL04I-EA-XBPM-02:SumAll:MeanValue_RBV') > self.XBPMSharedPVs.minXCurr.get() and
                self.fb_run_status.get() == 1
        ):
            if self.XBPMSharedPVs.fb_mode_status.get() == 1:
                self.set_run_status(1)
                self.print_function("Run for XBPM2 Started")

            elif self.XBPMSharedPVs.fb_mode_status.get() == 2:
                self.set_run_status(1)
                self.print_function("Run for XBPM2 Started")

        elif self.XBPMSharedPVs.fb_pause_status.get() == 0:
            self.set_run_status(2)
            self.print_function("Run for XBPM2 Paused")
        else:
            self.set_run_status(0)
            self.print_function("Run for XBPM2 Stopped")


if __name__ == '__main__':
    unittest.main()
