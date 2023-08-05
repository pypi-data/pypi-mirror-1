import unittest
import kforge.test.core.developer
import kforge.test.plugin.developer

def suite():
    suites = [
        kforge.test.core.developer.suite(),
        kforge.test.plugin.developer.suite(),
    ]
    return unittest.TestSuite(suites)
