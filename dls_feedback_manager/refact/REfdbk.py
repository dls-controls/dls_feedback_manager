from cothread import catools

class XBPM_DCMfeedback:

	def __init__(self, status=0):
		self.status = status
        status = [0, 1, 2]
        button_mnt = [fb_enable_status.name, fb_pause_status.name,
                      fb_fswt_output.name]
        xbpm_fbcheck = ['test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV',
                         'test:SR-DI-DCCT-01-SIGNAL', 'test:BL04I-PS-SHTR-01:STA']
        self.create_PV()
        self.feedback_status()

    def set_run_status(self, ):
        self.fb_run_status.set(status)

    def get_run_status(self):
        self.fb_run_status.get()

    def start_camonitors():
        catools.camonitor(button_mnt, checkFeedbackInputs)

    def xbpm_feedback_checks():
        catools.camonitor(xbpm_fbcheck, checkFeedbackInputs)

    def printfunction(printstatus, index):
        if index not in range(len(button_mnt)):
            print(printstatus)
        else:
            print(printstatus, button_mnt[index], index)


    def checkFeedbackInputs(self):
        if (
            catools.caget('test:BL04I-EA-XBPM-01:SumAll:MeanValue_RBV') > xbpm.minXCurr.get() and
            catools.caget('test:SR-DI-DCCT-01:SIGNAL') > xbpm.minSRCurr.get() and
            catools.caget('test:FE04I-PS-SHTR-02:STA') == 1 and
            catools.caget('test:BL04I-PS-SHTR-01:STA') == 1 and
            self.fb_enable_status.get() == 1 and
            self.fb_pause_status.get() == 1
        ):
            self.fb_run_status.set()
            self.printfunction()
        elif fb_pause_status.get() == 0:
            self.fb_run_status.set()
            self.printfunction()
        else:
            self.fb_run_status.set()
            self.printfunction()

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
        XBPM_DCMfeedback.__init__(self, status)
        xbpm_fbcheck = ['FE04I-PS-SHTR-02:STA', 'BL04I-EA-XBPM-02:SumAll:MeanValue_RBV']

    def checkFeedbackInputs(self):
        if (
            catools.caget('test:BL04I-EA-XBPM-02:SumAll:MeanValue_RBV') > myxbpmPVs.minXCurr.get() and
            fb_run_status.get() == 1 and
            fb_mode_status.get() == 1
        ):
            self.fb_run_status.get()
            #print("run2 start",camon_listFB[index], index)
        elif myxbpmPVs.fb_pause_status.get() == 0:
            self.fb_run_status.get()
            #print("run2 paused",camon_listFB[index], index)
        else:
            self.fb_run_status.get()
            #print("run2 stopped",camon_listFB[index], index)



    def xbpm_feedback_checks():
        catools.camonitor(xbpm_fbcheck, checkFeedbackInputs)




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



