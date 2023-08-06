import kforge.django.apps.kui.views.test.manipulator
import kforge.django.apps.kui.views.test.project
import kforge.django.apps.kui.views.test.person
import kforge.django.apps.kui.views.test.service
import kforge.django.apps.kui.views.test.member
import kforge.django.apps.kui.views.test.admin
import unittest

def suite():
    suites = [
        kforge.django.apps.kui.views.test.manipulator.suite(),
        kforge.django.apps.kui.views.test.project.suite(),
        kforge.django.apps.kui.views.test.person.suite(),
        kforge.django.apps.kui.views.test.service.suite(),
        kforge.django.apps.kui.views.test.member.suite(),
        kforge.django.apps.kui.views.test.admin.suite(),
    ]
    return unittest.TestSuite(suites)

