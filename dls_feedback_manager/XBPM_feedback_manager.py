import sys
from pkg_resources import require

require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from cothread import catools
from softioc import builder
from epicsdbbuilder import records, MS, CP, ImportRecord

if 'D' in sys.argv:
    def my_caput(pv, value, **args):
        print 'caput', pv, value, args

    catools.caput = my_caput


def Monitor(pv):
    return MS(CP(pv))


## PVs used by both DCMs (/FSWT).
class XBPMSharedPVs:

    ## Constructor.
    def __init__(self, beamline_num):
        self.beamline_num = beamline_num
        self.create_feedback_status_pv()
        self.create_xbpm_current()
        self.status_options = {0: 'Stopped', 1: 'Run', 2: 'Paused'}
        # For running monitors on overall ON/OFF button, GDA PAUSE button
        self.button_monitor = [self.fb_enable_status.name,
                               self.fb_pause_status.name]
        self.xbpm_fbcheck = [
            'BL' + self.beamline_num + 'I-EA-XBPM-01:SumAll:MeanValue_RBV',
            'SR-DI-DCCT-01-SIGNAL',
            'FE' + self.beamline_num + 'I-PS-SHTR-02:STA',
            'BL' + self.beamline_num + 'I-PS-SHTR-01:STA',
            'BL' + self.beamline_num + 'I-EA-XBPM-02:SumAll:MeanValue_RBV']

    ##  Restricts caput to given options.
    def validate_status_options(self):
        assert self.status_options in [0, 1, 2]

    ## Feedback status PVs.
    #  FB_ENABLE acts as an ON/OFF button for the IOC.
    #  FB_PAUSE pauses the IOC when a change to the TetrAMM is detected
    #  or when an energy change is requested.
    #  FB_MODE acts as a button for the different modes. The XBPMs can either
    #  run independently or in tandem.
    def create_feedback_status_pv(self):
        self.fb_enable_status = builder.mbbOut('FB_ENABLE',
                                               initial_value=0,
                                               PINI='YES',
                                               NOBT=2,
                                               ZRVL=0, ZRST='Stopped',
                                               ONVL=1, ONST='Run')

        self.fb_pause_status = builder.mbbOut('FB_PAUSE',
                                              initial_value=1,
                                              PINI='YES',
                                              NOBT=2,
                                              ZRVL=0, ZRST='Paused',
                                              ONVL=1, ONST='Ok to Run')

        self.fb_mode_status = builder.mbbOut('FB_MODE',
                                             initial_value=0,
                                             PINI='YES',
                                             NOBT=3,
                                             ZRVL=0, ZRST='Running on XBPM1',
                                             ONVL=1,
                                             ONST='Running on XBPM1 AND 2',
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
class XBPM1_Feedback:

    ## Constructor.
    #  Imports XBPMSharedPVs class and sets the prefix for XBPM1.
    #  Creates list of feedback prefixes.
    def __init__(self, XBPMSharedPVs, xbpm1_prefix, xbpm1_pid_params,
                 xbpm1_num, mode_range1):
        self.XBPMSharedPVs = XBPMSharedPVs
        self.prefix = xbpm1_prefix
        self.xbpm_pid_params = xbpm1_pid_params
        self.xbpm_num = xbpm1_num
        self.mode_range = mode_range1
        for pid in xbpm1_pid_params:
            pid[self.xbpm_pid_params.feedback_prefix] = self.prefix + ':' + \
                                            pid[self.xbpm_pid_params.feedback]
        print(self.prefix + " constructor successful")

    ## Create PVs and start camonitors
    def make_on_startup(self):
        self.run_status_pv()
        self.create_pid_pvs()
        self.set_feedback_pid()
        # For setting up the Feedback AUTO ON/OFF PV names
        self.caput_list = []
        for pid in self.xbpm_pid_params:
            self.caput_list.append(pid[self.xbpm_pid_params.feedback_prefix]
                                   + ':AUTOCALC.INPB')
            self.caput_list.append(pid[self.xbpm_pid_params.feedback_prefix] +
                                   ':AUTOCALC.INPC')
        self.setup_names()
        self.start_camonitors()

    ## Set up feedback auto on/off PV names
    def setup_names(self):
        catools.caput(self.caput_list, self.fb_run_status.name + ' CP')

    ## Sets run status to initial value
    def set_run_status(self, status):
        self.fb_run_status.set(self.XBPMSharedPVs.status_options[status])

    ## Created in the constructor.
    #  Used in check_feedback_inputs to specify conditions for setting new
    #  status if the PVs for DCM change.
    def run_status_pv(self):
        self.fb_run_status = builder.mbbOut('FB_RUN'+str(int(self.xbpm_num)),
                                            initial_value=0,
                                            PINI='YES',
                                            NOBT=2,
                                            ZRVL=0, ZRST='Stopped',
                                            ONVL=1, ONST='Run',
                                            TWVL=2, TWST='Paused')

    ## Created in constructor.
    #  Set limits for each PID parameter.
    def create_pid_pvs(self):
        self.pv_dict = {}
        for pid in self.xbpm_pid_params:
            self.pv_dict['KP' + pid[self.xbpm_pid_params.position]] = \
                builder.aIn(('KP' + pid[self.xbpm_pid_params.position]),
                            initial_value=pid[self.xbpm_pid_params.KP],
                            LOPR=-500.0,
                            HOPR=500.0,
                            PINI='YES')
            self.pv_dict['KI' + pid[self.xbpm_pid_params.position]] = \
                builder.aIn(('KI' + pid[self.xbpm_pid_params.position]),
                            initial_value=pid[self.xbpm_pid_params.KI],
                            LOPR=-500.0,
                            HOPR=500.0,
                            PINI='YES')
            self.pv_dict['KD' + pid[self.xbpm_pid_params.position]] = \
                builder.aIn(('KD' + pid[self.xbpm_pid_params.position]),
                            initial_value=pid[self.xbpm_pid_params.KD],
                            LOPR=-500.0,
                            HOPR=500.0,
                            PINI='YES')

    ## Monitor the feedback button PVs.
    def start_camonitors(self):
        catools.camonitor(self.XBPMSharedPVs.fb_enable_status.name,
                          self.check_enable_status)
        catools.camonitor(self.XBPMSharedPVs.button_monitor,
                          self.check_feedback_inputs)
        catools.camonitor(self.XBPMSharedPVs.xbpm_fbcheck,
                          self.check_feedback_inputs)

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
                catools.caget(
                    'BL' + self.XBPMSharedPVs.beamline_num +
                    'I-EA-XBPM-'+str(self.xbpm_num)+':SumAll:MeanValue_RBV')
                > self.XBPMSharedPVs.minXCurr.get() and
                catools.caget(
                    'SR-DI-DCCT-01:SIGNAL') > self.XBPMSharedPVs.minSRCurr.get()
                and
                catools.caget(
                    'FE' + self.XBPMSharedPVs.beamline_num + 'I-PS-SHTR-02:STA')
                == 1 and
                catools.caget(
                    'BL' + self.XBPMSharedPVs.beamline_num + 'I-PS-SHTR-01:STA')
                == 1 and
                self.XBPMSharedPVs.fb_enable_status.get() == 1 and
                self.XBPMSharedPVs.fb_pause_status.get() == 1 and
                self.XBPMSharedPVs.fb_mode_status.get() in self.mode_range
        ):
            self.set_run_status(1)
            print "Run for XBPM"+str(int(self.xbpm_num))+" Started"
        elif (self.XBPMSharedPVs.fb_enable_status.get() == 1 and
              self.XBPMSharedPVs.fb_pause_status.get() == 0 and
              self.XBPMSharedPVs.fb_mode_status.get() in self.mode_range
        ):
            self.set_run_status(2)
            print "Run for XBPM"+str(int(self.xbpm_num))+" Paused"
        else:
            self.set_run_status(0)
            print "Run for XBPM"+str(int(self.xbpm_num))+" Stopped"


    ## Set feedback PID values, and a scale if wanted.
    def set_feedback_pid(self):
        for pid in self.xbpm_pid_params:
            catools.caput(pid[self.xbpm_pid_params.feedback_prefix] + '.KP',
                          self.pv_dict['KP' + pid[
                              self.xbpm_pid_params.position]].get())
            catools.caput(pid[self.xbpm_pid_params.feedback_prefix] + '.KI',
                          self.pv_dict['KI' + pid[
                              self.xbpm_pid_params.position]].get())
            catools.caput(pid[self.xbpm_pid_params.feedback_prefix] + '.KD',
                          self.pv_dict['KD' + pid[
                              self.xbpm_pid_params.position]].get())


## XBPM2 feedback
class XBPM2_Feedback(XBPM1_Feedback):

    ## Constructor.
    #  Overrides prefix.
    #  Creates list of feedback prefixes.
    def __init__(self, XBPMSharedPVs, xbpm2_prefix, xbpm1_prefix,
                 xbpm2_pid_params, xbpm2_num, mode_range2):
        XBPM1_Feedback.__init__(self, XBPMSharedPVs, xbpm1_prefix,
                                xbpm2_pid_params, xbpm2_num, mode_range2)
        self.XBPMSharedPVs = XBPMSharedPVs
        self.prefix = xbpm2_prefix
        self.xbpm_pid_params = xbpm2_pid_params
        self.xbpm_num = xbpm2_num
        self.mode_range = mode_range2
        for pid in xbpm2_pid_params:
            pid[self.xbpm_pid_params.feedback_prefix] = self.prefix + ':' \
                                            + pid[self.xbpm_pid_params.prefix]
        print(self.prefix + " constructor successful")


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
