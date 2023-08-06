import unittest
import kforge.plugintest

def suite():
    suites = [
        kforge.plugintest.suite()
    ]
    return unittest.TestSuite(suites)

