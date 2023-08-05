import apple
import unittest
import doctest
#
def getTestSuite():
	suite = unittest.TestSuite()
	for mod in apple,:
	    suite.addTest(doctest.DocTestSuite(mod))
	return suite
#
runner = unittest.TextTestRunner()
runner.run(getTestSuite())
