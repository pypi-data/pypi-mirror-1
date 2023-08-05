import os.path
import commands
import unittest

from kforge.ioc import *
from kforge.apache.apacheconfig import ApacheConfigBuilder
import kforge.utils
from kforge.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(ApacheConfigBuilderTest),
#        unittest.makeSuite(VirtualHostBuilderTest),
    ]
    return unittest.TestSuite(suites)

def suiteCustomer():
    suites = [
        unittest.makeSuite(ApachectlConfigtestTest),
    ]
    return unittest.TestSuite(suites)

class ApacheConfigBuilderTest(TestCase):
    """
    We call setUp and tearDown in __init__ as we do not alter domain during
    run
    """
    
    def setUp(self):
        super(ApacheConfigBuilderTest, self).setUp()
        self.configBuilder = ApacheConfigBuilder()

   
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
        exp = '|^/person($|/.*)'
        self.failUnlessFragInFrag(exp, out)


class ApachectlConfigtestTest(ApacheConfigBuilderTest):

    def testAllConfig(self):
        # todo: Rewrite comment in English. Identify what 'this' is 
        # todo: and how it might be 'linked'.
        ## assumes you have linked this in so that Apache picks up the config
        ## file
        self.configBuilder.buildConfig()
        # todo: Move 'apachectl' assumption to system dictionary.
        # todo: Make apachectl script path configurable.
        cmd = 'apachectl configtest'
        status, output = commands.getstatusoutput(cmd)
        self.failUnless(not(status), output)

