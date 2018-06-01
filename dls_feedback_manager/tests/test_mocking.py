from pkg_resources import require
require('dls_feedback_manager==1.2')
from mock import patch


@patch('dls_feedback_manager.XBPMSharedPVs')
@patch('dls_feedback_manager.XBPM1_Feedback')
def test(MockXBPMSharedPVs, MockXBPM1_Feedback):
    dls_feedback_manager.XBPMSharedPVs()
    dls_feedback_manager.XBPM1_Feedback()
    assert MockXBPMSharedPVs is dls_feedback_manager.XBPMSharedPVs
    assert MockXBPM1_Feedback is dls_feedback_manager.XBPM1_Feedback
    assert MockXBPMSharedPVs.called
    assert MockXBPM1_Feedback.called


test()
