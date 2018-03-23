from cothread import catools
from softioc import builder


class XBPM_DCMfeedback:

    def __init__(self):
        self.status_options={'stop': 0, 'start': 1, 'pause': 2}
        self.button_mnt = [self.fb_enable_status.name, self.fb_pause_status.name]
        self.xbpm_fbcheck = ['test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV', 'test:SR-DI-DCCT-01-SIGNAL',
                             'test:BL04I-PS-SHTR-01:STA']
        self.caput_list=['BL04I-MO-DCM-01:FDBK1:AUTOCALC.INPB','BL04I-MO-DCM-01:FDBK2:AUTOCALC.INPB',
                'BL04I-MO-DCM-01:FDBK1:AUTOCALC.INPC','BL04I-MO-DCM-01:FDBK2:AUTOCALC.INPC']
        self.create_PVs()
        self.feedback_status()

    def setup_fb_auto_onoff_pvnames(self):
        catools.caput(self.caput_list, self.fb_run_status.name + ' CP')

    def set_run_status(self, status):
        self.fb_run_status.set(self.status_options[status])

    def get_run_status(self):
        self.fb_run_status.get()

    def start_camonitors(self):
        catools.camonitor(self.button_mnt, self.check_feedback_inputs)

    def xbpm_feedback_checks(self):
        catools.camonitor(self.xbpm_fbcheck, self.check_feedback_inputs)

    def printfunction(self, printstatus, index):
        if index not in range(len(self.button_mnt)):
            print(printstatus)
        else:
            print(printstatus, self.button_mnt[index], index)


    def check_feedback_inputs(self, index):
        if (
            catools.caget('test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV') > self.minXCurr.get() and
            catools.caget('test:SR-DI-DCCT-01:SIGNAL') > self.minSRCurr.get() and
            catools.caget('test:FE04I-PS-SHTR-02:STA') == 1 and
            catools.caget('test:BL04I-PS-SHTR-01:STA') == 1 and
            self.fb_enable_status.get() == 1 and
            self.fb_pause_status.get() == 1
        ):
            self.set_run_status('start')
            self.printfunction("run started", index)
        elif self.fb_pause_status.get() == 0:
            self.set_run_status('pause')
            self.printfunction("run paused", index)
        else:
            self.set_run_status('stop')
            self.printfunction("run stopped", index)

    def feedback_status(self):
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


class XBPM_FSWTfeedback(XBPM_DCMfeedback):

    def __init__(self):
        XBPM_DCMfeedback.__init__(self)
        self.monitored = [self.fb_enable_status.name, self.fb_pause_status.name, self.fb_fswt_output.name,
                          'FE04I-PS-SHTR-02:STA', 'BL04I-EA-XBPM-02:SumAll:MeanValue_RBV']
        self.caput_list = []
        self.create_PVs()
        self.feedback_status()

    def printfunction(self, printstatus, index):
        if index not in range(len(self.monitored)):
            print(printstatus)
        else:
            print(printstatus, self.monitored[index], index)

    def check_feedback_inputs(self, index):
        if (
            catools.caget('test:BL04I-EA-XBPM-02:SumAll:MeanValue_RBV') > self.minXCurr.get() and
            self.fb_run_status.get() == 1 and
            self.fb_mode_status.get() == 1
        ):
            self.set_run_status('start')
            self.printfunction("run started", index)
        elif self.fb_pause_status.get() == 0:
            self.set_run_status('pause')
            self.printfunction("run paused", index)
        else:
            self.set_run_status('stop')
            self.printfunction("run stopped", index)


    def xbpm_feedback_checks(self):
        catools.camonitor(self.xbpm_fbcheck, self.check_feedback_inputs)


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


XBPM_DCMfeedback()
XBPM_FSWTfeedback()
