import unittest
from kforge.testunit import ApplicationTestSuite

ApplicationTestSuite.buildApplication()

def run(suiteName=""):
    if not suiteName:
        import kforge.test
        suite = kforge.test.suite()
    else:
        suite = __import__(suiteName,'','','*').suite()
    unittest.TextTestRunner().run(suite)

