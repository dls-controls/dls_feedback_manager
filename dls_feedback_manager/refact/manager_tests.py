#!/bin/env dls-python

import REmyxbpmPVs
import unittest

class XBPM_manager_test(unittest.TestCase):

    def test_initial_variables(self):
        REmyxbpmPVs.XBPM1 = REmyxbpmPVs.XBPM_manager('BL04I-EA-XBPM-', 01, 50e-9, 100e-9, 1)
        self.assertEqual(REmyxbpmPVs.XBPM1.r0, 50e-9)
        self.assertNotEqual(REmyxbpmPVs.XBPM1.r0, 0)

    def test_initial_vars_2(self):
        REmyxbpmPVs.XBPM2 = REmyxbpmPVs.XBPM_manager('BL04I-EA-XBPM-', 02, 90e-9, 110e-9, 3.2)
        self.assertEqual(REmyxbpmPVs.XBPM2.XBPM_prefix, 'BL04I-EA-XBPM-', "these are equal")

    def test_xbpm_vals_name(self):
# test for combining parts together to form PV names



if __name__ == '__main__':
    unittest.main()
