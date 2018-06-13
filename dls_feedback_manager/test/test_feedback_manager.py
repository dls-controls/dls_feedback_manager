import unittest
from mock import MagicMock, patch, call
from XBPM_feedback_manager import XBPMSharedPVs, XBPM1Feedback, XBPM2Feedback

##  Unittests for XBPM Feedback Manager

XBPM_feedback_manager_patch = "XBPM_feedback_manager"
shared_patch = XBPM_feedback_manager_patch + ".XBPMSharedPVs"
XBPM1_patch = XBPM_feedback_manager_patch + ".XBPM1Feedback"
XBPM2_patch = XBPM_feedback_manager_patch + ".XBPM2Feedback"
catools_patch = XBPM_feedback_manager_patch + ".catools"

builder_mock = MagicMock()
beamline_num_mock = MagicMock()


class XBPMSharedPVsTester(XBPMSharedPVs):

    """A version of XBPM1Feedback without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)


class SharedParamsTest(unittest.TestCase):

    @patch(shared_patch + ".pause_condition")
    def test_feedback_status_pvs_called(self, pause_mock):

        XBPMSharedPVs(
            builder=builder_mock,
            beamline_num=beamline_num_mock).create_feedback_status_pv()

        builder_mock.mbbOut.assert_has_calls([
            call('FB_ENABLE',
                 initial_value=0,
                 PINI='YES',
                 NOBT=2,
                 ZRVL=0, ZRST='Stopped',
                 ONVL=1, ONST='Run'),
            call('FB_PAUSE',
                 initial_value=1,
                 PINI='YES',
                 NOBT=2,
                 ZRVL=0, ZRST='Paused',
                 ONVL=1, ONST='Ok to Run',
                 on_update=pause_mock,
                 always_update=True),
            call('FB_MODE',
                 initial_value=0,
                 PINI='YES',
                 NOBT=3,
                 ZRVL=0, ZRST='XBPM1 mode',
                 ONVL=1, ONST='XBPM1 AND 2 mode',
                 TWVL=2, TWST='XBPM2 mode')])

    @patch(shared_patch + ".pause_condition")
    def test_pause_condition_called(self, pause_mock):

        XBPMSharedPVs(
            builder=builder_mock,
            beamline_num=beamline_num_mock).pause_condition(0)

        pause_mock.assert_called_once_with(0)

    def test_xbpm_current_pvs_called(self):

        XBPMSharedPVs(
            builder=builder_mock,
            beamline_num=beamline_num_mock).create_xbpm_current()

        builder_mock.aIn.assert_has_calls([
            call('MIN_XBPMCURRENT',
                 initial_value=10e-9,
                 LOPR=0,
                 HOPR=1.0,
                 PINI='YES'),
            call('MIN_DCCTCURRENT',
                 initial_value=8,
                 LOPR=0,
                 HOPR=310.0,
                 PINI='YES')])


class XBPM1FeedbackTester(XBPM1Feedback):

    """A version of XBPM1Feedback without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)


## Testing functions
class MainClassFeedbackTests(unittest.TestCase):

    @patch(XBPM1_patch)
    def test_feedback_prefix_name(self):
        shared_pvs_mock = MagicMock()
        params_list_mock = MagicMock()

        XBPM1Feedback(
            builder=builder_mock, XBPMSharedPVs=shared_pvs_mock,
            xbpm1_pid_params_list=[params_list_mock],
            epics_fb_prefix1="prefix1", xbpm1_num="test1",
            mode_range1=(0, 10))

    @patch(catools_patch + ".caput")
    def test_setup_names_created(self, caput_mock):
        fb_status_mock = MagicMock()
        fb_status_mock.name = "FB_RUN1"
        xbpm1 = XBPM1FeedbackTester(
            caput_list=["TEST"],
            fb_run_status=fb_status_mock)

        xbpm1.setup_names()

        caput_mock.assert_called_once_with(["TEST"], "FB_RUN1 CP")

    @patch(catools_patch + ".caput")
    def test_set_feedback_pid_correct_names(self, caput_mock):
        patch_dict = {}
        params_list_mock = MagicMock()
        xbpm1 = XBPM1FeedbackTester(feedback_prefix="feedback_prefix",
                                    position=".POSX",
                                    pv_dict={patch_dict},
                                    xbpm_pid_params_list=[params_list_mock])

        xbpm1.set_feedback_pid()

        with patch.dict(
                patch_dict, {
                    "test_key1": "test_val1", "test_key2": "test_val2"}):
            assert patch_dict == {
                    "test_key1": "test_val1", "test_key2": "test_val2"}
            caput_mock.assert_called_once_with(
                "feedback_prefix.KP", patch_dict['KP.POSX'])

    @staticmethod
    def test_run_status_pv_called():
        xbpm1 = XBPM1FeedbackTester(
            builder=builder_mock,
            xbpm_num=1)

        xbpm1.run_status_pv()

        builder_mock.mbbOut.assert_called_once_with(
            'FB_RUN1',
            initial_value=0,
            PINI='YES',
            NOBT=2,
            ZRVL=0, ZRST='Stopped',
            ONVL=1, ONST='Run',
            TWVL=2, TWST='Paused')

    @patch(catools_patch + ".camonitor")
    def test_start_camonitors_called_x_times(self, camonitor_mock):  # x to no.
        shared_pvs_mock = MagicMock()
        enable_mock = MagicMock()
        enable_mock.name = "FB_ENABLE"
        feedback_inputs_mock = MagicMock()

        xbpm = XBPM1FeedbackTester(
            XBPMSharedPVs=shared_pvs_mock, status_monitor=["STATUS"],
            xbpm_fb_checklist=["SHUTTERS"], enable_status=enable_mock,
            feedback_inputs=feedback_inputs_mock)

        xbpm.start_camonitors()

        camonitor_mock.assert_has_calls([
            call("FB_ENABLE", enable_mock),
            call(["STATUS"], feedback_inputs_mock),
            call(["SHUTTERS"], feedback_inputs_mock)])


class XBPM2FeedbackTester(XBPM2Feedback):

    """A version of XBPM2Feedback without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)


class XBPM2FeedbackSuperTest(unittest.TestCase):

    @patch(XBPM1_patch + '.__init__')
    def test_super_called(self, super_mock):
        sharedpvs_class_mock = MagicMock()
        params_mock = MagicMock()

        XBPM2Feedback(
            builder=builder_mock,
            XBPMSharedPVs=sharedpvs_class_mock,
            xbpm2_pid_params_list=[params_mock],
            epics_fb_prefix2="prefix2", epics_fb_prefix1="prefix1",
            xbpm2_num='02', mode_range2=(0, 10))

        super_mock.assert_called_once_with(
            builder_mock, sharedpvs_class_mock, [params_mock],
            "prefix1", "02", (0, 10))
