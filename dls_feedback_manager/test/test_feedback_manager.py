import unittest
from mock import MagicMock, patch, call
from XBPM_feedback_manager import XBPMSharedPVs, XBPM1Feedback, XBPM2Feedback

## dls_feedback_manager
#  Unittests for XBPM Feedback Manager

XBPM_feedback_manager_patch = "XBPM_feedback_manager"
shared_patch = XBPM_feedback_manager_patch + ".XBPMSharedPVs"
XBPM1_patch = XBPM_feedback_manager_patch + ".XBPM1Feedback"
XBPM2_patch = XBPM_feedback_manager_patch + ".XBPM2Feedback"
catools_patch = XBPM_feedback_manager_patch + ".catools"


class XBPMSharedPVsTester(XBPMSharedPVs):

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)


class SharedParamsTest(unittest.TestCase):


    @patch(shared_patch)
    def test_feedback_status_pvs_created(self, status_mock):
        pass

    @patch(shared_patch)
    def test_xbpm_current_pvs_created(self, current_mock):
        pass

#current_mock.builder_mock.aIn.assert_has_calls
#[call("MIN_XBPMCURRENT"), call("MIN_DCCTCURRENT")])
# AN EXAMPLE, INSTEAD OF JUST NAME, PASS EVERYTHING THROUGH


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

    shared_mocked_names = ["fb_run_status"]

    @patch(catools_patch + ".caput")
    def test_setup_names(self, caput_mock):
        fb_status_mock = MagicMock()
        fb_status_mock.name = "FB_RUN1"
        xbpm1 = XBPM1FeedbackTester(
            caput_list=["TEST"],
            fb_run_status=fb_status_mock)

        xbpm1.setup_names()

        caput_mock.assert_called_once_with(["TEST"], "FB_RUN1 CP")

    def test_run_status_pv(self):
        builder_mock = MagicMock()
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

        # todo: for pid in params list


class XBPM2FeedbackTester(XBPM2Feedback):

    """A version of XBPM2Feedback without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)


class XBPMFeedbackSuperTest(unittest.TestCase):

    @patch(XBPM1_patch + '.__init__')
    def test_super_called(self, super_mock):
        builder_mock = MagicMock()
        sharedpvs_mock = MagicMock()
        params_mock = MagicMock()

        XBPM2Feedback(
            builder=builder_mock,
            XBPMSharedPVs=sharedpvs_mock,
            xbpm2_pid_params_list=[params_mock],
            epics_fb_prefix2="prefix2", epics_fb_prefix1="prefix1",
            xbpm2_num='02', mode_range2=(0, 1))

        super_mock.assert_called_once_with(
            builder_mock, sharedpvs_mock, [params_mock],
            "prefix1", "02", (0, 1))
