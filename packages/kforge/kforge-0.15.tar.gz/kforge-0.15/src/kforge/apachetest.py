import unittest
import kforge.apache.apacheconfigtest
import kforge.apache.urlpermissiontest

def suite():
    suites = [
        kforge.apache.apacheconfigtest.suite(),
        kforge.apache.urlpermissiontest.suite(),
    ]
    return unittest.TestSuite(suites)

