
from pkg_resources import require
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from cothread import catools
from softioc import builder
from epicsdbbuilder import records, MS, CP, ImportRecord

def Monitor(pv):
    return MS(CP(pv))

import unittest


## PVs used by both DCMs (/FSWT).
class XBPMSharedPVs:

    ## Constructor.
    def __init__(self, beamline_num, xbpm_pid_params):
        self.xbpm_pid_params = xbpm_pid_params
        self.beamline_num = beamline_num
        self.create_feedback_status_PV()
        self.create_xbpm_current()
        self.status_options = {0: 'Stopped', 1: 'Run', 2: 'Paused'}
        # For running monitors on overall ON/OFF button, GDA PAUSE button
        self.button_monitor = [self.fb_enable_status.name, self.fb_pause_status.name]

    ##  Restricts caput to anything other than options given.
    def validate_status_options(self):
        assert self.status_options in [0, 1, 2]

    ## Feedback status PVs.
    #  FB_ENABLE acts as an ON/OFF button for the IOC.
    #  FB_PAUSE pauses the IOC when a change to the TetrAMM is detected
    #  or when an energy change is requested.
    #  FB_MODE acts as a button for the different modes. The XBPMs can either
    #  run independently or in tandem.
    def create_feedback_status_PV(self):
        self.fb_enable_status = builder.mbbOut('FB_ENABLE',
                                               initial_value=0,
                                               PINI='YES',
                                               NOBT=2,
                                               ZRVL=0,   ZRST='Stopped',
                                               ONVL=1,   ONST='Run')

        self.fb_pause_status = builder.mbbOut('FB_PAUSE',
                                              initial_value=1,
                                              PINI='YES',
                                              NOBT=2,
                                              ZRVL=0,   ZRST='Paused',
                                              ONVL=1,   ONST='Ok to Run')

        self.fb_mode_status = builder.mbbOut('FB_MODE',
                                             initial_value=0,
                                             PINI='YES',
                                             NOBT=3,
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


    def topup_countdown(self):
        self.topup_countdown = builder.aOut('some pv name',
                                            initial_value=3)



## XBPM1 feedback
class XBPM1_feedback:

    ## Constructor.
    #  Imports XBPMSharedPVs class and sets the prefix for XBPM1.
    def __init__(self, XBPMSharedPVs, xbpm1_prefix):
        self.XBPMSharedPVs = XBPMSharedPVs
        self.prefix = xbpm1_prefix
        self.set_feedback_PID()

        print(self.prefix + " constructor successful")

    ## Create PVs and start camonitors
    def make_on_startup(self):
        self.create_PVs()
        self.create_PID_PVs()
        # For setting up the Feedback AUTO ON/OFF PV names
        self.caput_list = [self.prefix + ':FDBK1:AUTOCALC.INPB', self.prefix + ':FDBK2:AUTOCALC.INPB',
                           self.prefix + ':FDBK1:AUTOCALC.INPC', self.prefix + ':FDBK2:AUTOCALC.INPC']
        self.setup_names()
        # Run continuous checks for XBPM1
        self.xbpm_fbcheck = ['test:BL'+self.XBPMSharedPVs.beamline_num+'I-EA-XBPM-01:SumAll:MeanValue_RBV',
                             'test:SR-DI-DCCT-01-SIGNAL',
                             'test:BL'+self.XBPMSharedPVs.beamline_num+'I-PS-SHTR-01:STA']
        self.start_camonitors()

    ## Set up feedback auto on/off PV names
    def setup_names(self):
        catools.caput(self.caput_list, self.fb_run_status.name + ' CP')

    ## Sets run status to initial value
    def set_run_status(self, status):
        self.fb_run_status.set(self.XBPMSharedPVs.status_options[status])


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
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KPx1"],
                                LOPR=-500.0, HOPR=500.0, PINI='YES')
        self.kix1 = builder.aIn('KIX1',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KIx1"],
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kdx1 = builder.aIn('KDX1',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KDx1"],
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kpy1 = builder.aIn('KPY1',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KPy1"],
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kiy1 = builder.aIn('KIY1',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KIy1"],
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kdy1 = builder.aIn('KDY1',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KDy1"],
                                LOPR=-500, HOPR=500, PINI='YES')


    ## Monitor the feedback button PVs.
    def start_camonitors(self):
        catools.camonitor(self.XBPMSharedPVs.fb_enable_status.name, self.check_enable_status)
        catools.camonitor(self.XBPMSharedPVs.button_monitor, self.check_feedback_inputs)
        catools.camonitor(self.xbpm_fbcheck, self.check_feedback_inputs)
        #catools.camonitor(self.XBPMSharedPVs.topup_countdown, self.pause_for_topup)


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
    #  Mode has to set before turning enable on.
    def check_feedback_inputs(self, val, index):
        if (
            catools.caget('test:BL'+self.XBPMSharedPVs.beamline_num+'I-EA-XBPM-01:SumAll:MeanValue_RBV')
            > self.XBPMSharedPVs.minXCurr.get() and
            catools.caget('test:SR-DI-DCCT-01:SIGNAL') > self.XBPMSharedPVs.minSRCurr.get() and
            catools.caget('test:FE'+self.XBPMSharedPVs.beamline_num+'I-PS-SHTR-02:STA') == 1 and
            catools.caget('test:BL'+self.XBPMSharedPVs.beamline_num+'I-PS-SHTR-01:STA') == 1 and
            self.XBPMSharedPVs.fb_enable_status.get() == 1 and
            self.XBPMSharedPVs.fb_pause_status.get() == 1 and
            self.XBPMSharedPVs.fb_mode_status.get() in (0, 1)
        ): 
            self.set_run_status(1)
            print "Run for XBPM1 Started"
        elif (self.XBPMSharedPVs.fb_pause_status.get() == 0 and
            self.XBPMSharedPVs.fb_enable_status.get() == 1):
            if self.XBPMSharedPVs.fb_mode_status.get() == 2:
                self.set_run_status(0)
                print "Run for XBPM1 Stopped"
            else:
                self.set_run_status(2)
                print "Run for XBPM1 Paused"
        else:
            self.set_run_status(0)
            print "Run for XBPM1 Stopped"

    ## Set feedback PID values, and a scale if wanted.
    def set_feedback_PID(self):
        # Y XBPM1
        catools.caput(self.prefix+':FDBK1.KP', self.kpy1.get())
        catools.caput(self.prefix+':FDBK1.KI', self.kiy1.get())
        catools.caput(self.prefix+':FDBK1.KD', self.kdy1.get())
        # X XBPM1
        catools.caput(self.prefix+':FDBK2.KP', self.kpx1.get())
        catools.caput(self.prefix+':FDBK2.KI', self.kix1.get())
        catools.caput(self.prefix+':FDBK2.KD', self.kdx1.get())

    """## Pauses feedback when topping up electrons
    def pause_for_topup(self):
        if self.XBPMSharedPVs.topup_countdown.get() < 3:
            self.XBPMSharedPVs.fb_pause_status.set(0)
    """

## XBPM2 feedback
class XBPM2_feedback(XBPM1_feedback):

    ## Constructor.
    #  Overrides prefix.
    #  Recreates feedback enable and pause buttons.
    def __init__(self, XBPMSharedPVs, xbpm2_prefix, xbpm1_prefix):  # Solve prefix problem
        XBPM1_feedback.__init__(self, XBPMSharedPVs, xbpm1_prefix)
        self.XBPMSharedPVs = XBPMSharedPVs
        self.prefix = xbpm2_prefix

        print(self.prefix + " constructor successful")

    ## Create PVs and start camonitors
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
        self.xbpm_fbcheck = ['FE'+self.XBPMSharedPVs.beamline_num+'I-PS-SHTR-02:STA',
                             'BL'+self.XBPMSharedPVs.beamline_num+'I-EA-XBPM-02:SumAll:MeanValue:RBV']
        self.start_camonitors()


    ## Created in the constructor.
    #  Used in check_feedback_inputs to specify conditions for setting new status
    #  if XBPM2 change.
    def create_PVs(self):
        self.fb_run_status = builder.mbbOut('FB_RUN2',
                                            initial_value=0,
                                            PINI='YES',
                                            NOBT=2,
                                            ZRVL=0, ZRST='Stopped',
                                            ONVL=1, ONST='Run',
                                            TWVL=2, TWST='Paused')


    ## Created in constructor.
    #  Set limits for each PID parameter for XBPM2.
    def create_PID_PVs(self):
        self.kpx2 = builder.aIn('KPX2',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KPx2"],
                                LOPR=-500.0, HOPR=500.0, PINI='YES')
        self.kix2 = builder.aIn('KIX2',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KIx2"],
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kdx2 = builder.aIn('KDX2',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KDx2"],
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kpy2 = builder.aIn('KPY2',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KPy2"],
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kiy2 = builder.aIn('KIY2',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KIy2"],
                                LOPR=-500, HOPR=500, PINI='YES')
        self.kdy2 = builder.aIn('KDY2',
                                initial_value=self.XBPMSharedPVs.xbpm_pid_params["KDy2"],
                                LOPR=-500, HOPR=500, PINI='YES')


    ## Check the status of the ENABLE button for feedback.
    #  Set feedback on or off depending on mode, with printout to terminal.
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
                print "Feedback mode is XBPM2 operation only"
                self.set_run_status(1)


    ## What to do if any PVs change.
    #  Define conditions for setting run status.
    def check_feedback_inputs(self, val, index):
        if (catools.caget('test:BL'+self.XBPMSharedPVs.beamline_num+'I-EA-XBPM-02:SumAll:MeanValue_RBV')
                > self.XBPMSharedPVs.minXCurr.get() and
                self.fb_run_status.get() == 1
        ):
            if self.XBPMSharedPVs.fb_mode_status.get() in (1, 2):
                if self.XBPMSharedPVs.fb_pause_status.get() == 0:
                    self.set_run_status(2)
                    print "Run for XBPM2 Paused"
                else:
                    self.set_run_status(1)
                    print "Run for XBPM2 Started"
        elif (self.fb_run_status.get() == 2 and
              self.XBPMSharedPVs.fb_pause_status.get() == 1):
            self.set_run_status(1)
            print "Run for XBPM2 Started"
        else:
            self.set_run_status(0)
            print "Run for XBPM2 Stopped"

    ## Set feedback PID values, and a scale if wanted.
    def set_feedback_PID(self):
        # Y XBPM2
        catools.caput(self.prefix+':FDBK3.KP', self.kpy2.get())
        catools.caput(self.prefix+':FDBK3.KI', self.kiy2.get())
        catools.caput(self.prefix+':FDBK3.KD', self.kdy2.get())
        # X XBPM2
        catools.caput(self.prefix+':FDBK4.KP', self.kpx2.get())
        catools.caput(self.prefix+':FDBK4.KI', self.kix2.get())
        catools.caput(self.prefix+':FDBK4.KD', self.kdx2.get())


if __name__ == '__main__':
    unittest.main()
