import os.path
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

class ApacheConfigBuilderTest(TestCase):
    """
    We call setUp and tearDown in __init__ as we do not alter domain during
    run
    """
    
    def setUp(self):
        super(ApacheConfigBuilderTest, self).setUp()
        self.configBuilder = ApacheConfigBuilder()
    
    def testGetDefaultHostFragment(self):
        exp = 'ServerAlias ${domain_name} www.${domain_name}'
        self.failUnless(exp in self.configBuilder.getDefaultHostFragment())
    
    def testGetMediaHost(self):
        expPart = 'DocumentRoot ' + self.dictionary['www.media_root']
        mediaHost = self.configBuilder.getMediaHost()
        self.failUnless(expPart in mediaHost)
    
    def testGetAdminHostConfig(self):
        expPart = 'PythonHandler django.core.handlers.modpython'
        out = self.configBuilder.getAdminHostConfig()
        self.failUnless(expPart in out)
    
    def testGetProjectHostConfig(self):
        urlBuilder = kforge.url.UrlBuilderProject()
        expPart = 'DocumentRoot ' + urlBuilder.getWebRoot()
        out = self.configBuilder.getProjectHostConfig()
        self.failUnless(expPart in out)
    
    def testGetAccessControl(self):
        self.project = self.registry.projects['warandpeace']
        self.service = self.project.services['example']
        out = self.configBuilder.getAccessControl(self.service)
        expPart = 'AuthType Basic'
        self.failUnless(expPart in out)
    
    def testBuildConfig(self):
        self.configBuilder.buildConfig()
        self.failUnless(
            self.configBuilder.reloadConfig(), 'Reloading of apache failed'
        )
    
    def testDoVariableSubstitutionInString(self):
        pass # [[TODO: get tests from config builder]]


class VirtualHostBuilderTest(TestCase):

    def setUp(self):
        super(VirtualHostBuilderTest, self).setUp()
        self.vhost = apacheconfig.VirtualHostBuilder()
        self.hostFragment = """
            # Some Host Fragment Stuff
            """
        self.serverName = 'xyz.net'
        self.vhost.hostFragment = self.hostFragment
        self.vhost.serverName = self.serverName
    
    def testGetHttp(self):
        result = self.vhost.getHttp()
        self._commonTest(result)
    
    def _commonTest(self, result):
        self.failUnless(self.hostFragment in result)
        self.failUnless('ServerName ' + self.serverName in result)
        
    def testGetHttps(self):
        result = self.vhost.getHttps()
        self._commonTest(result)
        self.failUnless('SSLCertificateFile' in result)
    
    def testGetSslFragment(self):
        self.vhost.getSslFragment()
