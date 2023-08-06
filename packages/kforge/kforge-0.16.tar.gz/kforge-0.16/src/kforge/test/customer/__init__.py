import unittest
import kforge.test.core.customer
import kforge.test.plugin.customer

def suite():
    suites = [
        kforge.test.core.customer.suite(),
        kforge.test.plugin.customer.suite(),
    ]
    return unittest.TestSuite(suites)


