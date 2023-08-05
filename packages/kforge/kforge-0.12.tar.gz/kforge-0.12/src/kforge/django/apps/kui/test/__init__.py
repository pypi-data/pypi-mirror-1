from webunit import webunittest
import unittest
import kforge.django.apps.kui.views.test
from kforge.django.apps.kui.test.base import KuiTestCase
import kforge.django.apps.kui.test.admin
import kforge.django.apps.kui.test.person
import kforge.django.apps.kui.test.project
import kforge.django.apps.kui.test.member
import kforge.django.apps.kui.test.service

def suite():
    suites = [
        kforge.django.apps.kui.views.test.suite(),
        unittest.makeSuite(TestVisitServer),
        kforge.django.apps.kui.test.admin.suite(),
        kforge.django.apps.kui.test.person.suite(),
        kforge.django.apps.kui.test.project.suite(),
        kforge.django.apps.kui.test.member.suite(),
        kforge.django.apps.kui.test.service.suite(),
    ]
    return unittest.TestSuite(suites)

class TestVisitServer(KuiTestCase):
   
    def testHome(self):
        self.getAssertContent('/', 'Welcome to')
    
    def testUserLogin(self):
        self.getAssertContent('/login/', 'Log in')

