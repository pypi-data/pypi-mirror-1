import unittest

import kforge.testunit
import kforge.command.misc
from kforge.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestEmailNewPassword),
    ]
    return unittest.TestSuite(suites)

class TestEmailNewPassword(kforge.testunit.TestCase):

    def setUp(self):
        self.person = self.registry.persons['levin']
        self.oldPassword = self.person.name
        self.cmd = kforge.command.misc.EmailNewPassword(self.person.name)

    def tearDown(self):
        self.person.setPassword(self.oldPassword)

    def test_1(self):
        self.cmd.execute()
        self.failIf(self.person.isPassword(self.oldPassword))


