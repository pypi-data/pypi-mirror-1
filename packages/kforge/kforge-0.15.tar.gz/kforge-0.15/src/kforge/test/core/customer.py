import unittest
import kforge.apache.apacheconfigtest
import kforge.django.apps.kui.test

def suite():
    suites = [
        kforge.apache.apacheconfigtest.suiteCustomer(),
        kforge.django.apps.kui.test.suite(),
    ]
    return unittest.TestSuite(suites)

