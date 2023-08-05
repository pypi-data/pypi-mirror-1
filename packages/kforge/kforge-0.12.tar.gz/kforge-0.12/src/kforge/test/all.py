import unittest
import kforge.test
import kforge.django.apps.kui.test

def suite():
    suites = [
            kforge.test.suite(),                  # KForge Python package tests
            kforge.django.apps.kui.test.suite(),  # Apache with KForge tests
        ]
    return unittest.TestSuite(suites)

