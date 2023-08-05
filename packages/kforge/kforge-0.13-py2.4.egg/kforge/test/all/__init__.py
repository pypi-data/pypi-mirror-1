import unittest
import kforge.test.customer
import kforge.test.developer

def suite():
    suites = [
        kforge.test.customer.suite(),
        kforge.test.developer.suite(),
    ]
    return unittest.TestSuite(suites)

