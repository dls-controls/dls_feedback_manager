
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

builder.SetDeviceName('test')

class XBPM_DCMFeedback:
# XBPM1 feedback

    def make_on_start_up(self):
        self.create_PVs()
        self.create_PID_PVs()
        self.create_feedback_status_PV()
        # For running monitors on overall ON/OFF button, GDA PAUSE button
        self.button_monitor = [self.fb_enable_status.name, self.fb_pause_status.name]
        # Run continuous checks for XBPM1
        self.xbpm_fbcheck = ['test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV', 'test:SR-DI-DCCT-01-SIGNAL',
                             'test:BL04I-PS-SHTR-01:STA']
        self.start_camonitors()
        self.status_options={'Stopped': 0, 'Run': 1, 'Paused': 2}


    def __init__(self):
        self.make_on_start_up()
        self.prefix = 'test:BL04I-MO-DCM-01'

        # For setting up the Feedback AUTO ON/OFF PV names
        self.caput_list = [self.prefix + ':FDBK1:AUTOCALC.INPB', self.prefix + ':FDBK2:AUTOCALC.INPB',
                           self.prefix + ':FDBK1:AUTOCALC.INPC', self.prefix + ':FDBK2:AUTOCALC.INPC']
        print(self.prefix + " constructor successful")
        self.setup_names()

    def validate_params(self):
       assert self.status_options in [0, 1, 2]

    ## Set up feedback auto on/off PV names
    def setup_names(self):
        catools.caput(self.caput_list, self.fb_run_status.name + ' CP')

    def set_run_status(self, status):
        self.fb_run_status.set(self.status_options[status])

    def get_run_status(self):
        self.fb_run_status.get()

    def start_camonitors(self):
        catools.camonitor(self.button_monitor, self.check_feedback_inputs)
        catools.camonitor(self.xbpm_fbcheck, self.check_feedback_inputs)

    def print_function(self, printstatus, index):
        if index not in range(len(self.button_monitor)):
            print(printstatus)
        else:
            print(printstatus, self.button_monitor[index], index)

    # What to do if any PVs change
    def check_feedback_inputs(self, val, index):
        if (
            catools.caget('test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV') > self.minXCurr.get() and
            catools.caget('test:SR-DI-DCCT-01:SIGNAL') > self.minSRCurr.get() and
            catools.caget('test:FE04I-PS-SHTR-02:STA') == 1 and
            catools.caget('test:BL04I-PS-SHTR-01:STA') == 1 and
            self.fb_enable_status.get() == 1 and
            self.fb_pause_status.get() == 1
        ):
            self.set_run_status('Run')
            self.print_function("Run for XBPM1 Started", index)
        elif self.fb_pause_status.get() == 0:
            self.set_run_status('Paused')
            self.print_function("Run for XBPM1 Paused", index)
        else:
            self.set_run_status('Stopped')
            self.print_function("Run for XBPM1 Stopped", index)


    # Check the status of the ENABLE button for feedback.
    # Set feedback on or off as is appropriate.
    def check_enable_status(self, val):
    # SHOULD THIS VAL == STATUS OPTION?
        if val == 0:
            print "Feedback ENABLE button set to OFF (Stopped)"
            self.fb_enable_status.set(0)
        elif val == 1:
            print "Feedback ENABLE button set to ON (Running)"
            if self.fb_mode_status == 0:
                print "Feedback mode is XBPM1 operation only"
                self.fb_enable_status.set(1)
                # at this point, fswt should be set to 0
                # xbpm2 cant run on its own
            elif self.fb_mode_status == 1:
                print "Feedback mode is XBPM1 and XBPM2 operation"
                self.fb_enable_status(1)


    # What to do if any PVs change
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

        # Feedback mode PV, acts as button for the different modes (XBPM1, XBPM2)
        self.fb_mode_status = builder.mbbOut('FB_MODE',
                    initial_value = 1,
                    PINI = 'YES',
                    NOBT = 2,
                    ZRVL = 0,   ZRST = 'Running on XBPM1',
                    ONVL = 1,   ONST = 'Running on XBPM1 AND 2')


    def create_PVs(self):
        self.fb_run_status = builder.mbbOut('FB_RUN1',
                                       initial_value=0,
                                       PINI='YES',
                                       NOBT=2,
                                       ZRVL=0, ZRST='Stopped',
                                       ONVL=1, ONST='Run',
                                       TWVL=2, TWST='Paused')

        # Limits for XBPM current and DCCT current.
        self.minXCurr = builder.aIn('MIN_XBPMCURRENT',
                    initial_value = 10e-9,
                    LOPR = 0,
                    HOPR = 1.0,
                    PINI = 'YES')

        self.minSRCurr = builder.aIn('MIN_DCCTCURRENT',
                    initial_value = 8,
                    LOPR = 0,
                    HOPR = 310.0,
                    PINI = 'YES')


    def create_PID_PVs(self):
        self.kpx1 = builder.aIn('KPX1',
                           initial_value=KPx1,
                           LOPR=-500.0, HOPR=500.0, PINI='YES')
        self.kix1 = builder.aIn('KIX1',
                           initial_value=KIx1,
                           LOPR=0, HOPR=10.0, PINI='YES')
        self.kdx1 = builder.aIn('KDX1',
                           initial_value=KDx1,
                           LOPR=0, HOPR=10.0, PINI='YES')
        self.kpy1 = builder.aIn('KPY1',
                           initial_value=KPy1,
                           LOPR=0, HOPR=10.0, PINI='YES')
        self.kiy1 = builder.aIn('KIY1',
                           initial_value=KIy1,
                           LOPR=0, HOPR=10.0, PINI='YES')
        self.kdy1 = builder.aIn('KDY1',
                           initial_value=KDy1,
                           LOPR=0, HOPR=10.0, PINI='YES')


class XBPM_FSWTfeedback(XBPM_DCMFeedback):
# XBPM2 feedback
    def __init__(self):
        XBPM_DCMFeedback.__init__(self)
        self.prefix = 'BL04I-MO-FSWT-01'

        # For running monitors on overall ON/OFF button, GDA PAUSE button, FSWT feedback output button
        self.button_monitor = [self.fb_enable_status.name, self.fb_pause_status.name, self.fb_fswt_output.name]

        # Run continuous checks for XBPM2
        self.xbpm_fbcheck = ['FE04I-PS-SHTR-02:STA', 'BL04I-EA-XBPM-02:SumAll:MeanValue:RBV']

        # For setting up feedback AUTO ON/OFF PV names
        self.caput_list = [self.prefix + ':FDBK1:AUTOCALC.INPB', self.prefix + ':FDBK2:AUTOCALC.INPB',
                           self.prefix + ':FDBK1:AUTOCALC.INPC', self.prefix + ':FDBK2:AUTOCALC.INPC',
                           self.prefix + ':FDBK3:AUTOCALC.INPB', self.prefix + ':FDBK4:AUTOCALC.INPB',
                           self.prefix + ':FDBK3:AUTOCALC.INPC', self.prefix + ':FDBK4:AUTOCALC.INPC']


    def check_feedback_inputs(self, val, index):
        if (
            catools.caget('test:BL04I-EA-XBPM-02:SumAll:MeanValue_RBV') > self.minXCurr.get() and
            self.fb_run_status.get() == 1 and
            self.fb_mode_status.get() == 1
        ):
            self.set_run_status('Run')
            self.print_function("Run started", index)
        elif self.fb_pause_status.get() == 0:
            self.set_run_status('Paused')
            self.print_function("Run paused", index)
        else:
            self.set_run_status('Stopped')
            self.print_function("Run stopped", index)

    # Check the status of the ENABLE button for feedback.
    # Set feedback on or off as is appropriate.
    def check_enable_status(self, val):
        # SHOULD THIS VAL == STATUS OPTION?
        if val == 0:
            print "Feedback ENABLE button set to OFF (Stopped)"
            self.fb_enable_status.set(0)
        elif val == 1:
            if self.fb_mode_status == 0:
                print "Feedback mode is XBPM1 operation only"
                self.fb_enable_status.set(0)
            elif self.fb_mode_status == 1:
                print "Feedback ENABLE button set to ON (Running)"
                print "Feedback mode is XBPM1 and XBPM2 operation"
                self.fb_enable_status.set(1)
        else:
            assert 0<=val<=1, "Enable button fail"

    def enable_status_checker(self):
    # Makes sure that if FSWT is on, DCM is also on
    # Otherwise, if DCM is off, FSWT is also off
        if XBPM_DCMFeedback.create_feedback_status_PV(self.fb_enable_status == 0):
            assert XBPM_FSWTfeedback.create_feedback_status_PV(self.fb_enable_status(0)), "Both XBPM1 and XBPM2 are off"
        elif XBPM_FSWTfeedback.create_feedback_status_PV(self.fb_enable_status(1)):
            assert XBPM_DCMFeedback.create_feedback_status_PV(self.fb_enable_status(1)), "Both XBPM1 and XBPM2 are on"

    def create_PVs(self):

        self.fb_run_status = builder.mbbOut('FB_RUN2',
                                    initial_value=0,
                                    PINI='YES',
                                    NOBT=2,
                                    ZRVL=0, ZRST='Stopped',
                                    ONVL=1, ONST='Run',
                                    TWVL=2, TWST='Paused')

        # Limits for XBPM current and DCCT current.
        self.minXCurr = builder.aIn('MIN_XBPMCURRENT',
                                initial_value = 10e-9,
                                LOPR = 0,
                                HOPR = 1.0,
                                PINI = 'YES')

        # Feedback FWST mode PV, acts as button for the different actuators (UPSTREAM, DOWNSTREAM)
        self.fb_fswt_output = builder.mbbOut('FB_FSWTOUTPUT',
                                    initial_value = 1,
                                    PINI = 'YES',
                                    NOBT = 2,
                                    ZRVL = 0,   ZRST = 'Upstream actuator',
                                    ONVL = 1,   ONST = 'Downstream actuator')


    def create_PID_PVs(self):
        self.kpx2 = builder.aIn('KPX2',
                           initial_value=KPx2,
                           LOPR=-500.0, HOPR=500.0, PINI='YES')
        self.kix2 = builder.aIn('KIX2',
                           initial_value=KIx2,
                           LOPR=0, HOPR=10.0, PINI='YES')
        self.kdx2 = builder.aIn('KDX2',
                           initial_value=KDx2,
                           LOPR=0, HOPR=10.0, PINI='YES')
        self.kpy2 = builder.aIn('KPY2',
                           initial_value=KPy2,
                           LOPR=0, HOPR=10.0, PINI='YES')
        self.kiy2 = builder.aIn('KIY2',
                           initial_value=KIy2,
                           LOPR=0, HOPR=10.0, PINI='YES')
        self.kdy2 = builder.aIn('KDY2',
                           initial_value=KDy2,
                           LOPR=0, HOPR=10.0, PINI='YES')


if __name__ == '__main__':
    unittest.main()
