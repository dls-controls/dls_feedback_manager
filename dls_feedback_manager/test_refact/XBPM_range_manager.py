from pkg_resources import require
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

import unittest

from softioc import builder
from cothread import catools

from epicsdbbuilder import records, MS, CP, ImportRecord

def Monitor(pv):
    return MS(CP(pv))

class range_manager:

    def __init__(self, XBPM_prefix='BL04I-EA-XBPM-', XBPM_num='00', lower_current_limit=0.0, upper_current_limit=0.0, scale_factor=0.0, threshold_percentage=0.0):
        # scale_factor is the magnification of the optics lens (XBPM2)
        self.XBPM_prefix = XBPM_prefix
        self.XBPM_num = XBPM_num
        self.lower_current_limit = lower_current_limit
        self.upper_current_limit = upper_current_limit
        self.scale_factor = scale_factor
        self.threshold_percentage = threshold_percentage
        self.validate_params()
        self.xbpm_vals()

    def validate_params(self):
        assert type(self.scale_factor) is not str, "input numerical scale factor "
        assert type(self.threshold_percentage) is not str, "input numerical threshold percentage"
        assert 0 <= self.threshold_percentage <= 100, "insert valid percentage"

    def xbpm_vals(self):
# Imported records
        self.dx_mean_value = ImportRecord(self.XBPM_prefix + (self.XBPM_num) + ':DiffX:MeanValue_RBV')
        self.sx_mean_value = ImportRecord(self.XBPM_prefix + (self.XBPM_num) + ':SumX:MeanValue_RBV')
        self.dy_mean_value = ImportRecord(self.XBPM_prefix + (self.XBPM_num) + ':DiffY:MeanValue_RBV')
        self.sy_mean_value = ImportRecord(self.XBPM_prefix + (self.XBPM_num) + ':SumY:MeanValue_RBV')
        self.xbpm_sum_mean_value = ImportRecord(self.XBPM_prefix + (self.XBPM_num) + ':SumAll:MeanValue_RBV')
        self.xbpm_x_beamsize = ImportRecord(self.XBPM_prefix + (self.XBPM_num) + ':DRV:PositionScaleX')
        self.xbpm_y_beamsize = ImportRecord(self.XBPM_prefix + (self.XBPM_num) + ':DRV:PositionScaleY')


    def norm(self):
# "Normalised" position PVs
        self.xbpm_normx = records.calc('XBPM'+str(int(self.XBPM_num))+'_NORMX', CALC='A/B',
                               INPA = Monitor(self.dx_mean_value),
                               INPB = Monitor(self.sx_mean_value),
                               LOPR = -1,
                               HOPR = 1,
                               PINI = 'YES',
                               EGU = '')

        self.xbpm_normy = records.calc('XBPM'+str(int(self.XBPM_num))+'_NORMY', CALC='A/B',
                               INPA = Monitor(self.dy_mean_value),
                               INPB = Monitor(self.sy_mean_value),
                               LOPR = -1,
                               HOPR = 1,
                               PINI = 'YES',
                               EGU = '')


    def position_threshold(self):
        # XBPM position threshold PVs
        self.threshold_percentage_xbpm = builder.aOut('THRESHOLDPC_XBPM'+str(int(self.XBPM_num)),
                                                       initial_value=self.threshold_percentage,
                                                       LOPR=0,
                                                       HOPR=100,
                                                       PINI='YES')

        self.position_threshold_ok_xbpm = records.calc('XBPM'+str(int(self.XBPM_num))+'POSITION_OK', CALC='(ABS(B)<(A/100)) && (ABS(C)<(A/100))',
                                                        INPA=Monitor(self.threshold_percentage_xbpm),
                                                        INPB=Monitor(self.xbpm_normx),
                                                        INPC=Monitor(self.xbpm_normy),
                                                        LOPR=0,
                                                        HOPR=1,
                                                        PINI='YES',
                                                        EGU='')

    def camonitor_range(self):
        # check XBPM signal currents
        catools.camonitor(self.XBPM_prefix + (self.XBPM_num)+':SumAll:MeanValue_RBV', self.check_range)
        catools.camonitor(self.XBPM_prefix + (self.XBPM_num)+':SumAll:MeanValue_RBV', self.check_range)


    def check_range(self, val):
        # current range for flipping between tetramms - can be redefined in new pvs if necessary
        self.r = catools.caget(self.XBPM_prefix + (self.XBPM_num) + ':DRV:Range')
        if self.r == 0:  # 120uA
            if val < self.lower_current_limit:
                # Won't flip into 'higher current mode' until current is higher than lower_current_limit
                catools.caput(self.XBPM_prefix + (self.XBPM_num) + ':DRV:Range', 1)
        elif self.r == 1:  # 120nA
            if val > self.upper_current_limit:
                # Won't flip into 'lower current mode' until current is lower than upper_current_limit
                catools.caput(self.XBPM_prefix + (self.XBPM_num) + 'DRV:Range', 0)


    def camonitor_scale(self):
        # Run monitor on the ID gap. XBPM1; change scale factors if ID energy changes.
        catools.camonitor('BL04I-MO-DCM-01:ENERGY', self.set_vertical_XBPM_scale_factor)


    def set_vertical_XBPM_scale_factor(self, energy):
        #
        # Set the vertical XBPM scale factor [um] based on the DCM energy [keV]
        # This maths is based on the beam size calculation from the I04 undulator. For
        # more information please see TDI-DIA-XBPM-REP-003.
        # Note - XBPM2 divided by 3.2
        ky = (-26 * energy + 1120) / self.scale_factor
        kx = 1200 / self.scale_factor
        catools.caput(self.XBPM_prefix + (self.XBPM_num) + ':DRV:PositionScaleY', ky)
        catools.caput(self.XBPM_prefix + (self.XBPM_num) + ':DRV:PositionScaleX', kx)


    def curr_limits(self):
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


    def signals_ok(self):
        # XBPM signal chain check PVs
        self.xbpmSignalsOk = records.calc('XBPM' + str(int(self.XBPM_num)) + 'SIGNALS_OK', CALC='A>B',
                                          INPA=Monitor(self.xbpm_sum_mean_value),
                                          INPB=Monitor(self.minXCurr),
                                          LOPR=0,
                                          HOPR=1,
                                          PINI='YES',
                                          EGU='')


if __name__ == '__main__':
    unittest.main()


"""
IOC_NAME = 'test:BL04I-EA-%s-01'

builder.SetDeviceName(IOC_NAME % 'FDBK') """