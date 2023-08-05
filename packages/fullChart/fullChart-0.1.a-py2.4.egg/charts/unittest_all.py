import genTriggers, mosixDataStore, mosixChart
import doctest
import unittest

def getTestSuite():
	suite = unittest.TestSuite()
	for mod in genTriggers, mosixChart, mosixDataStore,:
		#print mod
		suite.addTest(doctest.DocTestSuite(mod))
	return suite

#print dir(unittest)
runner = unittest.TextTestRunner()
runner.run(getTestSuite())

