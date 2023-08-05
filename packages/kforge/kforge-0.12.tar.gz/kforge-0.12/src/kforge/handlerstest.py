import unittest
import kforge.handlers.apachecodestest
import kforge.handlers.modpythontest
import kforge.handlers.projecthosttest

def suite():
    suites = [
        kforge.handlers.apachecodestest.suite(),
        kforge.handlers.modpythontest.suite(),
        kforge.handlers.projecthosttest.suite(),
    ]
    return unittest.TestSuite(suites)

