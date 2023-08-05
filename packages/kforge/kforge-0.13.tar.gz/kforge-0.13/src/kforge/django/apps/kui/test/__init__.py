from webunit import webunittest
import unittest
from kforge.django.apps.kui.test.base import KuiTestCase
import kforge.django.apps.kui.test.admin
import kforge.django.apps.kui.test.person
import kforge.django.apps.kui.test.project
import kforge.django.apps.kui.test.member
import kforge.django.apps.kui.test.service

def suite():
    suites = [
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
        offset = self.url_scheme.url_for('home')
        self.getAssertContent(offset, 'Welcome to')
    
    def testUserLogin(self):
        offset = self.url_scheme.url_for('login')
        self.getAssertContent(offset, 'Log in')

