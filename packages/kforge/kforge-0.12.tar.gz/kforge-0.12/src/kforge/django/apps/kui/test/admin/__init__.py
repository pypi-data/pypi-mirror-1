from kforge.django.apps.kui.test.base import KuiTestCase
import kforge.django.apps.kui.test.admin.domainObject
import kforge.django.apps.kui.test.admin.hasMany
import unittest

def suite():
    suites = [
        kforge.django.apps.kui.test.admin.domainObject.suite(),
        kforge.django.apps.kui.test.admin.hasMany.suite(),
    ]
    return unittest.TestSuite(suites)

