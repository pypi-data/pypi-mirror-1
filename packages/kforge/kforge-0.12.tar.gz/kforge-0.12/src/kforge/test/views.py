import unittest
import kforge.testunit
import kforge.django.apps.kui.views.test

def suite():
    suites = [
        kforge.django.apps.kui.views.test.suite(),
    ]
    return unittest.TestSuite(suites)

