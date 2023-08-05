import unittest

import kforge.django.apps.kui.test

def suite():
    suites = [
        kforge.django.apps.kui.test.suite(),
    ]
    return unittest.TestSuite(suites)

