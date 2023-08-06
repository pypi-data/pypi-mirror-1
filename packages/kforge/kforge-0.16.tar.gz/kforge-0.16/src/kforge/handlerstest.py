import unittest
import kforge.handlers.apachecodestest
import kforge.handlers.modpythontest

def suite():
    suites = [
        kforge.handlers.apachecodestest.suite(),
        kforge.handlers.modpythontest.suite(),
    ]
    return unittest.TestSuite(suites)

