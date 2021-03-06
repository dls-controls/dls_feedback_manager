from pkg_resources import require
import logging
require('cothread==2.14')
require('numpy==1.11.1')
require('epicsdbbuilder==1.2')

#from softioc import builder
from cothread import catools
from epicsdbbuilder import records, MS, CP, ImportRecord

def Monitor(pv):
    return MS(CP(pv))


## XBPM range manager
class XBPMRangeManager(object):

    ## Constructor.
    #  Inputs from XBPM manager control replace defaults.
    def __init__(
            self, builder, shared_pvs, tetramm_prefix='', xbpm_num='',
            lower_current_limit=0.0, upper_current_limit=0.0,
            optics=0.0, threshold_percentage=0.0, id_energy=''):
        self.builder = builder
        self.shared_pvs = shared_pvs
        self.tetramm_prefix = tetramm_prefix
        self.xbpm_num = xbpm_num
        self.lower_current_limit = lower_current_limit
        self.upper_current_limit = upper_current_limit
        self.optics = optics
        self.threshold_percentage = threshold_percentage
        self.id_energy = id_energy
        self.call_on_start()
        if len(id_energy) > 0:
            self.camonitor_scale()

    ## Creates PVs and starts camonitors.
    def call_on_start(self):
        self.xbpm_vals()
        self.norm_pos()
        self.position_threshold()
        self.validate_params()
        self.signals_ok()
        self.camonitor_range()

        logging.debug('PVs made and camonitors started')

    ## Sets restrictions for input values
    def validate_params(self):
        assert type(self.optics) is not str, \
            "input numerical type optics"
        assert type(self.threshold_percentage) is not str, \
            "input numerical type threshold percentage"
        assert 0 <= self.threshold_percentage <= 100, "insert valid percentage"
        assert 01 <= int(self.xbpm_num) <= 9

    ## Imported records of readback values
    def xbpm_vals(self):
        self.dx_mean_value = ImportRecord(self.tetramm_prefix +
            str(self.xbpm_num) + ':DiffX:MeanValue_RBV')
        self.sx_mean_value = ImportRecord(self.tetramm_prefix +
            str(self.xbpm_num) + ':SumX:MeanValue_RBV')
        self.dy_mean_value = ImportRecord(self.tetramm_prefix +
            str(self.xbpm_num) + ':DiffY:MeanValue_RBV')
        self.sy_mean_value = ImportRecord(self.tetramm_prefix +
            str(self.xbpm_num) + ':SumY:MeanValue_RBV')
        self.xbpm_sum_mean_value = ImportRecord(self.tetramm_prefix +
            str(self.xbpm_num) + ':SumAll:MeanValue_RBV')
        self.xbpm_x_beamsize = ImportRecord(self.tetramm_prefix +
            str(self.xbpm_num) + ':DRV:PositionScaleX')
        self.xbpm_y_beamsize = ImportRecord(self.tetramm_prefix +
            str(self.xbpm_num) + ':DRV:PositionScaleY')

    ## "Normalised" beam position PVs
    def norm_pos(self):
        self.xbpm_normx = records.calc(
            'XBPM'+str(int(self.xbpm_num))+'_NORMX',
            CALC='A/B',
            INPA=Monitor(self.dx_mean_value),
            INPB=Monitor(self.sx_mean_value),
            LOPR=-1,
            HOPR=1,
            PINI='YES',
            EGU='')

        self.xbpm_normy = records.calc(
            'XBPM'+str(int(self.xbpm_num))+'_NORMY',
            CALC='A/B',
            INPA=Monitor(self.dy_mean_value),
            INPB=Monitor(self.sy_mean_value),
            LOPR=-1,
            HOPR=1,
            PINI='YES',
            EGU='')

    ## XBPM position threshold PVs
    #  Checks if the beam position is ok before restarting data collection.
    def position_threshold(self):
        self.threshold_percentage_xbpm = self.builder.aOut(
            'THRESHOLDPC_XBPM' + str(int(self.xbpm_num)),
            initial_value=self.threshold_percentage,
            LOPR=0,
            HOPR=100,
            PINI='YES')

        self.position_threshold_ok_xbpm = records.calc(
            'XBPM' + str(int(self.xbpm_num)) + 'POSITION_OK',
            CALC='(ABS(B)<(A/100)) && (ABS(C)<(A/100))',
            INPA=Monitor(self.threshold_percentage_xbpm),
            INPB=Monitor(self.xbpm_normx),
            INPC=Monitor(self.xbpm_normy),
            LOPR=0,
            HOPR=1,
            PINI='YES',
            EGU='')

    def signals_ok(self):
        self.xbpmSignalsOk = records.calc(
            'XBPM' + str(int(self.xbpm_num)) + 'SIGNALS_OK',
            CALC='A>B',
            INPA=Monitor(self.xbpm_sum_mean_value),
            INPB=Monitor(self.shared_pvs.minXCurr),
            LOPR=0,
            HOPR=1,
            PINI='YES',
            EGU='')

    ## Monitor XBPM signal currents.
    def camonitor_range(self):
        catools.camonitor(self.tetramm_prefix + self.xbpm_num +
                          ':SumAll:MeanValue_RBV', self.check_range)

    ## Gets current range for flipping between TetrAMM current ranges
    def check_range(self, val):
        self.r = catools.caget(
            self.tetramm_prefix + self.xbpm_num + ':DRV:Range')
        if self.r == 0:  # 120uA
            if val < self.lower_current_limit:
                catools.caput(
                    self.tetramm_prefix + str(self.xbpm_num) + ':DRV:Range', 1)
                logging.info("Current range set to +-120nA")
        elif self.r == 1:  # 120nA
            if val > self.upper_current_limit:
                catools.caput(
                    self.tetramm_prefix + str(self.xbpm_num) + ':DRV:Range', 0)
                logging.info("Current range set to +-120uA")

    ## Run monitor on the ID gap, change scale factors if ID energy changes.
    def camonitor_scale(self):
        catools.camonitor(self.id_energy, self.set_vertical_xbpm_scale_factor)

    ## Set the vertical XBPM scale factor [um] based on the DCM energy [keV]
    #  Scale_factor is the magnification of the optics lens (XBPM2)
    #  This maths is based on the beam size calculation from the I04 undulator.
    #  For more information please see TDI-DIA-XBPM-REP-003.
    #  Note - XBPM2 divided by 3.2
    def set_vertical_xbpm_scale_factor(self, energy):
        ky = (-26 * energy + 1120) / self.optics
        kx = 1200 / self.optics
        catools.caput(self.tetramm_prefix + str(self.xbpm_num) +
                      ':DRV:PositionScaleY', ky)
        logging.info("Position scale Y set to " + str(ky))
        catools.caput(self.tetramm_prefix + str(self.xbpm_num) +
                      ':DRV:PositionScaleX', kx)
        logging.info("Position scale X set to " + str(kx))
