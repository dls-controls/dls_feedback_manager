#!/bin/env dls-python

import REmyxbpmPVs
import unittest



class XBPM_manager_test(unittest.TestCase):

    def test(self):
        assert False

    def test_initial_variables(self):
        XBPM1 = REmyxbpmPVs.XBPM_manager('BL04I-EA-XBPM-', 01, 90e-9, 110e-9, 1)
        self.assertEqual(XBPM1.r0, 90e-9)
        self.assertNotEqual(XBPM1.r0, 0)

    def test_initial_vars_2(self):
        XBPM2 = REmyxbpmPVs.XBPM_manager('BL04I-EA-XBPM-', 02, 90e-9, 110e-9, 3.2)
        self.assertEqual(XBPM2.XBPM_prefix, 'BL04I-EA-XBPM-', "these are equal")

    def test_xbpm_vals_name(self):
        pass
# test for combining parts together to form PV names


if __name__ == '__main__':
    unittest.main()
