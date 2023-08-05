import genTriggers
import doctest
import unittest

def getTestSuite():
	suite = unittest.TestSuite()
	for mod in genTriggers,:
		#print mod
		suite.addTest(doctest.DocTestSuite(mod))
	return suite

#print dir(unittest)
runner = unittest.TextTestRunner()
runner.run(getTestSuite())

import os
os.remove('./test/testtriggers.db.temp')
os.remove('./test/testtriggersNOCASCADE.db.temp')

