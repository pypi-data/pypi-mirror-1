import unittest
import kforge.test.core.developer

def suite():
    suites = [
        kforge.test.core.developer.suite(),
    ]
    return unittest.TestSuite(suites)


