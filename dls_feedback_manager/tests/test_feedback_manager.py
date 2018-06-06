#!/bin/env dls-python

import unittest
from mock import Mock, MagicMock, patch
from XBPM_feedback_manager import XBPM1Feedback, XBPM2Feedback

## dls_feedback_manager
#  Unittests for XBPM Feedback Manager.

XBPM_feedback_manager_patch = "XBPM_feedback_manager"
XBPM2 = XBPM_feedback_manager_patch + ".XBPM2Feedback"
catools_patch = XBPM_feedback_manager_patch + ".catools"



class XBPM1FeedbackTester(XBPM1Feedback):

    """A version of XBPM1Feedback without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)


## Testing functions
class FeedbackTests(unittest.TestCase):

    @patch(catools_patch + ".caput")
    def test_setup_names(self, caput_mock):
        status_mock = MagicMock()
        status_mock.name = "FB_RUN1"
        xbpm1 = XBPM1FeedbackTester(caput_list=["TEST"],
                                   fb_run_status=status_mock)

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

    @patch(XBPM2 + '.__init__')
    def test_super_called(self, super_mock):
        builder_mock = MagicMock()
        sharedpvs_mock = MagicMock()
        xbpm2 = XBPM2FeedbackTester(builder=builder_mock,
                                    XBPMSharedPVs=sharedpvs_mock,
                                    xbpm2_pid_params_list=["TEST"],
                                    epics_fb_prefix1="prefix1",
                                    epics_fb_prefix2="prefix2",
                                    xbpm2_num="02", mode_range2=(0, 1))

        xbpm2.__init__()

        super_mock.assert_called_once_with(builder_mock, sharedpvs_mock,
                                           ["TEST"], "prefix2", "prefix1",
                                           "02", (0, 1))
