from pkg_resources import require
require('cothread==2.14')
require('numpy==1.13.3')
require('epicsdbbuilder==1.2')

import unittest

from softioc import builder
from cothread import catools

from epicsdbbuilder import records, MS, CP, ImportRecord

def Monitor(pv):
    return MS(CP(pv))

class XBPM_manager:

    def __init__(self, XBPM_prefix='BL04I-EA-XBPM-', XBPM_num=0, r0=float(0), r1=float(0), sf=float(0)):
        # r0 & r1 are limits for the current, resulting in flipping between tetramms
        # These currents can be predefined in new PVs if necessary
        # sf is the magnification of the optics lens (XBPM2)
        self.XBPM_prefix = XBPM_prefix
        self.XBPM_num = XBPM_num
        self.r0 = r0
        self.r1 = r1
        self.sf = sf


    def xbpm_vals(self):

        self.dx_mean_value = ImportRecord(self.XBPM_prefix + str(self.XBPM_num) + ':DiffX:MeanValue_RBV')
        self.sx_mean_value = ImportRecord(self.XBPM_prefix + str(self.XBPM_num) + ':SumX:MeanValue_RBV')
        self.dy_mean_value = ImportRecord(self.XBPM_prefix + str(self.XBPM_num) + ':DiffY:MeanValue_RBV')
        self.sy_mean_value = ImportRecord(self.XBPM_prefix + str(self.XBPM_num) + ':SumY:MeanValue_RBV')
        self.xbpm_sum_mean_value = ImportRecord(self.XBPM_prefix + str(self.XBPM_num) + ':SumAll:MeanValue_RBV')
        self.xbpm_x_beamsize = ImportRecord(self.XBPM_prefix + str(self.XBPM_num) + ':DRV:PositionScaleX')
        self.xbpm_y_beamsize = ImportRecord(self.XBPM_prefix + str(self.XBPM_num) + ':DRV:PositionScaleY')


    def normal(self):

        self.xbpm_normx = records.calc('XBPM'+str(self.XBPM_num)+'_NORMX', CALC='A/B',
                               INPA = Monitor(self.dx_mean_value),
                               INPB = Monitor(self.sx_mean_value),
                               LOPR = -1,
                               HOPR = 1,
                               PINI = 'YES',
                               EGU = '')
        self.xbpm_normy = records.calc('XBPM'+str(self.XBPM_num)+'_NORMY', CALC='A/B',
                               INPA = Monitor(self.dy_mean_value),
                               INPB = Monitor(self.sy_mean_value),
                               LOPR = -1,
                               HOPR = 1,
                               PINI = 'YES',
                               EGU = '')


    def position_threshold(self):
        # XBPM position threshold PVs
        self.threshold_percentage_xbpm1 = builder.aOut('THRESHOLDPC_XBPM1',
                                                       initial_value=3,
                                                       LOPR=0,
                                                       HOPR=100,
                                                       PINI='YES')

        self.threshold_percentage_xbpm2 = builder.aOut('THRESHOLDPC_XBPM2',
                                                       initial_value=3,
                                                       LOPR=0,
                                                       HOPR=100,
                                                       PINI='YES')

        self.position_threshold_ok_xbpm1 = records.calc('XBPM1POSITION_OK', CALC='(ABS(B)<(A/100)) && (ABS(C)<(A/100))',
                                                        INPA=Monitor(self.threshold_percentage_xbpm1),
                                                        INPB=Monitor(self.xbpm_normx),
                                                        INPC=Monitor(self.xbpm_normy),
                                                        LOPR=0,
                                                        HOPR=1,
                                                        PINI='YES',
                                                        EGU='')

        self.position_threshold_ok_xbpm2 = records.calc('XBPM2POSITION_OK', CALC='(ABS(B)<(A/100)) && (ABS(C)<(A/100))',
                                                        INPA=Monitor(self.threshold_percentage_xbpm2),
                                                        INPB=Monitor(self.xbpm_normx),
                                                        INPC=Monitor(self.xbpm_normy),
                                                        LOPR=0,
                                                        HOPR=1,
                                                        PINI='YES',
                                                        EGU='')


    def camonitor_range(self):
        # check XBPM signal currents
        catools.camonitor('test:' + self.XBPM_prefix + str(self.XBPM_num)+':SumAll:MeanValue_RBV', self.check_range)
        catools.camonitor('test:' + self.XBPM_prefix + str(self.XBPM_num)+':SumAll:MeanValue_RBV', self.check_range)


    def check_range(self, val):

        self.r = catools.caget('test:' + self.XBPM_prefix + str(self.XBPM_num) + ':DRV:Range')
        if self.r == 0:  # 120uA
            if val < self.r0:
                # Won't flip into 'higher/lower current mode' until current is higher/lower than r0
                catools.caput(self.XBPM_prefix + str(self.XBPM_num) + ':DRV:Range', 1)
        elif self.r == 1:  # 120nA
            if val > self.r1:
                # Won't flip into 'higher/lower current mode' until current is higher/lower than r1
                catools.caput(self.XBPM_prefix + str(self.XBPM_num) + 'DRV:Range', 0)


    def camonitor_scale(self):
        # Run monitor on the ID gap. XBPM1; change scale factors if ID energy changes.
        catools.camonitor(self.XBPM_prefix + str(self.XBPM_num)+':ENERGY', self.setVerticalXBPMScaleFactor)


    def setVerticalXBPMScaleFactor(self, energy):
        # Set the vertical XBPM scale factor [um] based on the DCM energy [keV]
        # This maths is based on the beam size calculation from the I04 undulator. For
        # more information please see TDI-DIA-XBPM-REP-003.
        # Note - XBPM2 divided by 3.2
        ky = (-26 * energy + 1120) / self.sf
        kx = 1200 / self.sf
        catools.caput(self.XBPM_prefix + str(self.XBPM_num) + ':DRV:PositionScaleY', ky)
        catools.caput(self.XBPM_prefix + str(self.XBPM_num) + ':DRV:PositionScaleX', kx)


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
        self.xbpmSignalsOk = records.calc('XBPM' + str(self.XBPM_num) + 'SIGNALS_OK', CALC='A>B',
                                          INPA=Monitor(self.xbpm_sum_mean_value),
                                          INPB=Monitor(self.minXCurr),
                                          LOPR=0,
                                          HOPR=1,
                                          PINI='YES',
                                          EGU='')


if __name__ == '__main__':
    unittest.main()

    XBPM1 = XBPM_manager('BL04I-EA-XBPM-', 01, 90e-9, 110e-9, 1)
    XBPM2 = XBPM_manager('BL04I-EA-XBPM-', 02, 90e-9, 110e-9, 3.2)

    list_of_XBPMs = [XBPM1, XBPM2]

    for i in list_of_XBPMs:
        i.xbpm_vals()



# class that inherits from XBPM manager, derived classes = scale factor and range


"""
IOC_NAME = 'test:BL04I-EA-%s-01'

builder.SetDeviceName(IOC_NAME % 'FDBK') """
