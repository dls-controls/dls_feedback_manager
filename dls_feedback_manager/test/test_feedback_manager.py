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
            beamline_num=beamline_num_mock).pause_condition(1)

        pause_mock.assert_called_once_with(1)

    # write test to make sure called when necessary, include other def which
    # calls it

    @patch(XBPM_feedback_manager_patch + ".logging")
    def test_pause_condition_logging(self, logging_mock):

        XBPMSharedPVs(
            builder=builder_mock, beamline_num="03").pause_condition(0)
        self.assertTrue(logging_mock.warning.called)

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
    def test_feedback_prefix_name(self, class_patch):  # todo
        shared_pvs_mock = MagicMock()
        params_list_mock = MagicMock()

        XBPM1Feedback(
            builder=builder_mock, XBPMSharedPVs=shared_pvs_mock,
            xbpm1_pid_params_list=[params_list_mock],
            epics_fb_prefix1="prefix1", xbpm1_num="01",
            mode_range1=(0, 10))

        class_patch.assert_called_once_with(
            builder_mock, shared_pvs_mock, [params_list_mock], "prefix1",
            "01", (0, 10))

    @patch(catools_patch + ".caput")
    def test_setup_names_created(self, caput_mock):
        fb_status_mock = MagicMock()
        fb_status_mock.name = "FB_RUN1"
        xbpm1 = XBPM1FeedbackTester(
            caput_list=["TEST"],
            fb_run_status=fb_status_mock)

        xbpm1.setup_names()

        caput_mock.assert_called_once_with(["TEST"], "FB_RUN1 CP")

    def test_run_status_pv_called(self):
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

    def test_set_run_status(self):
        pass

    def test_pid_pvs_created(self):
        pass

    @patch(catools_patch + ".caput")  # todo
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

    # test that both enable and pause from status monitor get passed through
    # camonitor from "start camonitors"

    @patch(XBPM1_patch + ".logging")
    def test_xbpm1_enable_status_logging(self):
        pass


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
