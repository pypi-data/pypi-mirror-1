import os.path
import commands
import unittest

from kforge.ioc import *
from kforge.apache.apacheconfig import ApacheConfigBuilder
import kforge.utils
from kforge.testunit import TestCase
from kforge.dictionarywords import APACHE_CONFIGTEST_CMD
from kforge.dictionary import SystemDictionary

#todo: Rename ApacheConfigBuilderTest to TestApacheConfigBuilder.
#todo: Rename test cases with Test-postfix to have Test-prefix.
#todo: Agree importance of consistent code style.
#todo: Agree that diverging style goes against the grain and is unhelpful.

def suite():
    suites = [
        unittest.makeSuite(TestApacheConfigBuilder),
    ]
    return unittest.TestSuite(suites)

def suiteCustomer():
    suites = [
        unittest.makeSuite(ApachectlConfigtestTest),
    ]
    return unittest.TestSuite(suites)

class TestApacheConfigBuilder(TestCase):
    """
    We call setUp and tearDown in __init__ as we do not alter domain during
    run
    """
    
    def setUp(self):
        super(TestApacheConfigBuilder, self).setUp()
        self.configBuilder = ApacheConfigBuilder()
        self.dictionary = SystemDictionary()
   
    def failUnlessFragInFrag(self, expectedFragment, configFragment):
        self.failUnless(expectedFragment in configFragment, "%s not in %s" % (
            expectedFragment, configFragment
        ))
    
    def testGetAdminHostConfig(self):
        expFrag = 'PythonHandler django.core.handlers.modpython'
        configFrag = self.configBuilder.getAdminHostConfig()
        self.failUnlessFragInFrag(expFrag, configFrag)

    def testGetAccessControl(self):
        self.project = self.registry.projects['warandpeace']
        self.service = self.project.services['example']
        expFrag = 'AuthType basic'
        configFrag = self.configBuilder.getAccessControl(self.service)
        self.failUnlessFragInFrag(expFrag, configFrag)

    def test_getDjangoHandledPaths(self):
        out = self.configBuilder.getDjangoHandledPaths()
        exp = '^/$|'
        self.failUnlessFragInFrag(exp, out)
        exps = [ '|^/person($|/.*)',
                '|^/admin($|/.*)',
                '|^/project($|/.*)',
                '|^/login($|/.*)',
                '|^/logout($|/.*)',
                '|^/accessDenied($|/.*)',
                ]
        for exp in exps:
            self.failUnlessFragInFrag(exp, out)


class ApachectlConfigtestTest(TestApacheConfigBuilder):
    '''KForge generated config file must be being loaded by Apache
       as o/w test does nothing.
    '''

    def testAllConfig(self):
        self.configBuilder.buildConfig()
        # todo: Move 'apachectl' assumption to system dictionary.
        # todo: Make apachectl script path configurable.
        cmd = self.dictionary[APACHE_CONFIGTEST_CMD]
        status, output = commands.getstatusoutput(cmd)
        self.failUnless(not(status), output)

