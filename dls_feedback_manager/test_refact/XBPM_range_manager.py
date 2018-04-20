from pkg_resources import require
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

from softioc import builder
from cothread import catools

from epicsdbbuilder import records, MS, CP, ImportRecord

def Monitor(pv):
    return MS(CP(pv))

import unittest

class RangeManager:

    ## Constructor.
    def __init__(self, xbpm_prefix='', xbpm_num='', lower_current_limit=0.0, upper_current_limit=0.0,
                        scale_factor=0.0, threshold_percentage=0.0, id_energy=''):
        self.xbpm_prefix = xbpm_prefix
        self.xbpm_num = xbpm_num
        self.lower_current_limit = lower_current_limit
        self.upper_current_limit = upper_current_limit
        self.scale_factor = scale_factor
        self.threshold_percentage = threshold_percentage
        self.id_energy = id_energy
        self.make_pvs()
        self.validate_params()
        self.xbpm_vals()
        self.camonitor_range()
        if len(id_energy) > 0:
            self.camonitor_scale()


        print(self.xbpm_prefix + self.xbpm_num + ' constructor successful')


    def make_pvs(self):
        self.norm()
        self.position_threshold()
        self.curr_limits()
        self.signals_ok()


    ## Sets restrictions for input values
    def validate_params(self):
        assert type(self.scale_factor) is not str, "input numerical type scale factor"
        assert type(self.threshold_percentage) is not str, "input numerical type threshold percentage"
        assert 0 <= self.threshold_percentage <= 100, "insert valid percentage"
        assert 01 <= int(self.xbpm_num) <= 9


    ## Imported records of readback values
    def xbpm_vals(self):

        self.dx_mean_value = ImportRecord(self.xbpm_prefix + self.xbpm_num + ':DiffX:MeanValue_RBV')
        self.sx_mean_value = ImportRecord(self.xbpm_prefix + self.xbpm_num + ':SumX:MeanValue_RBV')
        self.dy_mean_value = ImportRecord(self.xbpm_prefix + self.xbpm_num + ':DiffY:MeanValue_RBV')
        self.sy_mean_value = ImportRecord(self.xbpm_prefix + self.xbpm_num + ':SumY:MeanValue_RBV')
        self.xbpm_sum_mean_value = ImportRecord(self.xbpm_prefix + self.xbpm_num + ':SumAll:MeanValue_RBV')
        self.xbpm_x_beamsize = ImportRecord(self.xbpm_prefix + self.xbpm_num + ':DRV:PositionScaleX')
        self.xbpm_y_beamsize = ImportRecord(self.xbpm_prefix + self.xbpm_num + ':DRV:PositionScaleY')


    ## "Normalised" position PVs
    def norm(self):

        self.xbpm_normx = records.calc('XBPM'+str(int(self.xbpm_num))+'_NORMX', CALC='A/B',
                                       INPA=Monitor(self.dx_mean_value),
                                       INPB=Monitor(self.sx_mean_value),
                                       LOPR=-1,
                                       HOPR=1,
                                       PINI='YES',
                                       EGU='')

        self.xbpm_normy = records.calc('XBPM'+str(int(self.xbpm_num))+'_NORMY', CALC='A/B',
                                       INPA=Monitor(self.dy_mean_value),
                                       INPB=Monitor(self.sy_mean_value),
                                       LOPR=-1,
                                       HOPR=1,
                                       PINI='YES',
                                       EGU='')


    ## XBPM position threshold PVs
    def position_threshold(self):

        self.threshold_percentage_xbpm = builder.aOut('THRESHOLDPC_XBPM'+str(int(self.xbpm_num)),
                                                      initial_value=self.threshold_percentage,
                                                      LOPR=0,
                                                      HOPR=100,
                                                      PINI='YES')

        self.position_threshold_ok_xbpm = records.calc('XBPM'+str(int(self.xbpm_num))+'POSITION_OK',
                                                       CALC='(ABS(B)<(A/100)) && (ABS(C)<(A/100))',
                                                       INPA=Monitor(self.threshold_percentage_xbpm),
                                                       INPB=Monitor(self.xbpm_normx),
                                                       INPC=Monitor(self.xbpm_normy),
                                                       LOPR=0,
                                                       HOPR=1,
                                                       PINI='YES',
                                                       EGU='')

    ## Limits for XBPM current and DCCT current.
    def curr_limits(self):
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

    ## XBPM signal chain check PVs
    def signals_ok(self):
        self.xbpmSignalsOk = records.calc('XBPM' + str(int(self.xbpm_num)) + 'SIGNALS_OK', CALC='A>B',
                                          INPA=Monitor(self.xbpm_sum_mean_value),
                                          INPB=Monitor(self.minXCurr),
                                          LOPR=0,
                                          HOPR=1,
                                          PINI='YES',
                                          EGU='')


    ## Monitor XBPM signal currents.
    def camonitor_range(self):
        catools.camonitor(self.xbpm_prefix + self.xbpm_num +':SumAll:MeanValue_RBV', self.check_range)
        catools.camonitor(self.xbpm_prefix + self.xbpm_num +':SumAll:MeanValue_RBV', self.check_range)


    ## Gets current range for flipping between tetramm current ranges
    #  Won't flip into 'higher current range' until current is higher than lower_current_limit
    #  Won't flip into 'lower current range' until current is lower than upper_current_limit
    def check_range(self, val):
        self.r = catools.caget(self.xbpm_prefix + self.xbpm_num + ':DRV:Range')
        if self.r == 0:  # 120uA
            if val < self.lower_current_limit:
                catools.caput(self.xbpm_prefix + self.xbpm_num + ':DRV:Range', 1)
                print("Current range set to +-120nA")
        elif self.r == 1:  # 120nA
            if val > self.upper_current_limit:
                catools.caput(self.xbpm_prefix + self.xbpm_num + ':DRV:Range', 0)
                print("Current range set to +-120uA")


    ## Run monitor on the ID gap. XBPM1; change scale factors if ID energy changes.
    def camonitor_scale(self):
        catools.camonitor(self.id_energy, self.set_vertical_xbpm_scale_factor)


    ## Set the vertical XBPM scale factor [um] based on the DCM energy [keV]
    #  Scale_factor is the magnification of the optics lens (XBPM2)
    #  This maths is based on the beam size calculation from the I04 undulator. For
    #  more information please see TDI-DIA-XBPM-REP-003.
    #  Note - XBPM2 divided by 3.2
    def set_vertical_xbpm_scale_factor(self, energy):
        ky = (-26 * energy + 1120) / self.scale_factor
        kx = 1200 / self.scale_factor
        catools.caput(self.xbpm_prefix + self.xbpm_num + ':DRV:PositionScaleY', ky)
        print("Position scale Y set to " + str(ky))
        catools.caput(self.xbpm_prefix + self.xbpm_num + ':DRV:PositionScaleX', kx)
        print("Position scale X set to " + str(kx))


    def complete(self):
        print('Range manager for ' + self.xbpm_prefix + self.xbpm_num + ' done')


if __name__ == '__main__':
    unittest.main()
