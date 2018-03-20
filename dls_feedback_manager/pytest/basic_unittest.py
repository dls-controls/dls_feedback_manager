#!/bin/env dls-python

import unittest

def calc(x,y):
	return x+y

def return_none():
    return None

class numtest(unittest.TestCase):

	def test_answer(self):
		self.assertEqual(calc(2,3), 5)
		self.assertNotEqual(calc(2,3),4)

	def test_same(self):
		x = 9, y = 10
		self.assertIsNot(x, y, "x should not be equal to y")

	def test_zero(self):	
		x = y = 0
		self.assertIs(calc(x,y),0, "ans should be bigger than zero")	

        def test_none(self):
                self.assertIsNone(return_none(), "should be none")

#        def test_not_none(self):
#                self.assertIsNotNone(return_none(), "should not be none")

	def test_neg(self):
		x = -4
		y = -8
		self.assertGreater(x, y, "answer cant be negative")
				
	def test_type(self):
		x = 5
		y = 7
		self.assertTrue(type(x)==int and type(y)==int)
		x = "hello"
		y = "bye"
		self.assertFalse(type(x) and type(y)!=str)
		self.assertRaises(TypeError, "x y are integers only")
			
if __name__ == '__main__':
	unittest.main()
