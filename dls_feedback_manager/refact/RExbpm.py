"""
m pkg_resources import require
require('cothread==2.13')
require('numpy==1.11.1')
require('epicsdbbuilder==1.0')

from softioc import builder

from epicsdbbuilder import records, MS, CP, ImportRecord

def Monitor(pv):
    return MS(CP(pv)) """

#initial PID paramaters for XBPM1 and XBPM2, del dict['pv'] and reassign if necessary
pid_params_dict={'KPx1':-1.800e-4,'KIx1':1.250,'KDx1':0.000,'KPy1':1.0e-5,'KIy1':1.1042,'KDy1':0.000,
		'KPx2':-5.670e-5,'KIx2':2.791,'KDx2':0.0,'KPy2':1.080E-4,'KIy2':3.636,'KDy2':0.0}

LOPR = 0
HOPR = 10
PINI = 'YES'

#records to import

#def records_calcs	

#	def mbbOut_params(name, val, PINI, NOBT, ZRVL, ZRST, ONVL, ONST, TWVL, TWST):

class create_pvs:

	def __init__(self, name):
		self.name = name
		#want name to be each key in dict then want each to be assigned the args below:

	def pid_aIn_params(name, val, LOPR, HOPR, PINI):
		for item in pid_params_list:
			pv_name = name
			initial_value = pid_params_list
			LOPR = 0
			HOPR = 10
			PINI = 'YES'

