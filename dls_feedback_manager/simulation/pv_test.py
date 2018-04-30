#!/bin/env dls-python

import time
from pkg_resources import require
require('cothread==2.13')

from cothread import catools
import cothread

my_list=['SFX44126-PY-IOC-01:KPX1','SFX44126-PY-IOC-01:FB_ENABLE','SFX44126-PY-IOC-01:THRESHOLDPC_XBPM1']


#list of pvs from simulationtest.py
def test_start_camonitor():
    # XBPM1 feedback check (RUN1):
    catools.camonitor(my_list, test_checkFeedbackInputs)
    #catools.camonitor('SFX44126-PY-IOC-01:FB_ENABLE', test_checkFeedbackInputs)
    #catools.camonitor('SFX44126-PY-IOC-01:THRESHOLDPC_XBPM1', test_checkFeedbackInputs)


#callback function from second arg in test_start_camonitor
#as list of pvs in prev fn, need index arg
def test_checkFeedbackInputs(value, index):
    #'SFX44126-PY-IOC-01:KPX1') > xbpm.minXCurr.get()

    print(value, my_list[index])



if __name__ == "__main__": # only works when run from terminal
    test_start_camonitor()
    while 1==1:     # always runs until manually killed in terminal
        cothread.Sleep(1)
