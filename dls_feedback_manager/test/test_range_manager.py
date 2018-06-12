import unittest
from mock import MagicMock, patch, call
from XBPM_range_manager import XBPMRangeManager

## Unittests for XBPM Range Manager

XBPM_range_manager_patch = "XBPM_range_manager"
range_manager_class_patch = XBPM_range_manager_patch + ".XBPMRangeManager"
catools_patch = XBPM_range_manager_patch + ".catools"

builder_mock = MagicMock()
records_mock = MagicMock()


class RangeManagerTester(XBPMRangeManager):

    """A version of XBPMRangeManager without initialisation.

    For testing single methods of the class. Must have required attributes
    passed before calling testee function.

    """

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            self.__setattr__(attribute, value)


class RangeMainTests(unittest.TestCase):

    @patch(range_manager_class_patch + ".__init__")
    def test_constructor_args(self, constructor_mock):  #todo
        shared_pvs_mock = MagicMock()

        XBPMRangeManager(
            builder=builder_mock, shared_pvs=shared_pvs_mock,
            tetramm_prefix="tetramm", xbpm_num='01',
            lower_current_limit=1.0, upper_current_limit=10.0,
            optics=1.0, threshold_percentage=5.0,
            id_energy="idenergy")

        constructor_mock.assert_called_once_with(
            builder_mock, shared_pvs_mock,
            "tetramm", "01", 1.0, 10.0, 1.0, 5.0, "idenergy")

    def test_assertion_errors_for_incorrect_values(self):
        pass

    def test_records_imported(self):  #todo
        import_mock = MagicMock()
        dx_mean_val_mock = MagicMock
        xbpm1 = RangeManagerTester(
            dx_mean_value=dx_mean_val_mock,
            ImportRecord=import_mock,
            tetramm_prefix="tetramm",
            xbpm_num=1)

        xbpm1.xbpm_vals()

        import_mock.assert_called_once_with("tetramm1:DiffX:MeanValue_RBV")

    def test_records_calc_called_twice(self):  #todo
        monitor_mock = MagicMock()
        dx_mean_val_mock = MagicMock()
        sx_mean_val_mock = MagicMock()

        norm1 = RangeManagerTester(
            builder=builder_mock, records=records_mock,
            xbpm_num=1)

        norm1.norm_pos()

        records_mock.calc.assert_called_once_with(
            'XBPM1_NORMX',
            CALC='A/B',
            INPA=monitor_mock(dx_mean_val_mock),
            INPB=monitor_mock(sx_mean_val_mock),
            LOPR=-1,
            HOPR=1,
            PINI='YES',
            EGU='')

    def test_norm_called_in_pos_threshold(self):
        pass

    def test_builder_record_called_once_each(self):
        pass

    @patch(catools_patch + ".camonitor")
    def test_camonitor_range(self, camonitor_mock):
        check_range_mock = MagicMock()
        xbpm1 = RangeManagerTester(
            tetramm_prefix="tetramm", xbpm_num="01",
            check_range=check_range_mock)

        xbpm1.camonitor_range()

        camonitor_mock.assert_called_once_with(
            "tetramm01:SumAll:MeanValue_RBV", check_range_mock)

    @patch(catools_patch + ".caput")
    @patch(catools_patch + ".caget")
    def test_check_range(self, caput_mock, caget_mock):
        xbpm1 = RangeManagerTester(
            r=0, tetramm_prefix="tetramm", xbpm_num="01",
            lower_current_limit=1, upper_current_limit=3)

        xbpm1.check_range(val=0.5)

        caget_mock.assert_called_once_with("tetramm01:DRV:Range")
        caput_mock.assert_called_once_with("tetramm01:DRV:Range", 1)

    @patch(catools_patch + ".camonitor")
    def test_camonitor_scale(self, camonitor_mock):
        set_scale_mock = MagicMock()
        xbpm1 = RangeManagerTester(
            id_energy="energy pv",
            set_vertical_xbpm_scale_factor=set_scale_mock)

        xbpm1.camonitor_scale()

        camonitor_mock.assert_called_once_with(
            "energy pv", set_scale_mock)

    @patch(catools_patch + ".caput")
    def test_vertical_scale_factor_caput_calls_and_values(self, caput_mock):

        io4 = RangeManagerTester(
            optics=3.2, tetramm_prefix="tetramm", xbpm_num=1)

        io4.set_vertical_xbpm_scale_factor(energy=1)

        caput_mock.assert_has_calls([
            call("tetramm1:DRV:PositionScaleY", 341.875),
            call("tetramm1:DRV:PositionScaleX", 375.0)])

    def test_XBPM_num_not_1_or_2(self):
        pass

    def test_initial_variable_inputs(self):
        pass

    def test_invalid_threshold_percentage(self):
        pass