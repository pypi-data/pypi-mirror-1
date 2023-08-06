import unittest

from kforge.testunit import TestCase
import kforge.filesystem

def suite():
    suites = [
            unittest.makeSuite(PluginTest),
        ]
    return unittest.TestSuite(suites)

class PluginTest(TestCase):
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not self.registry.plugins.has_key('www'):
            self.registry.plugins.create('www')
        self.plugin = self.registry.plugins['www']
        self.project = self.registry.projects['annakarenina']
        if 'www' in self.project.services:
            service = self.project.services['www']
            service.delete()
            service.purge()
        self.project.services.create('www', plugin=self.plugin)
        self.service = self.project.services['www']
        self.fsPathBuilder = kforge.filesystem.FileSystemPathBuilder()
    
    def tearDown(self):
        self.service.delete()
        self.service.purge()
    
    def testHasInstalledServicePath(self):
        path = self.fsPathBuilder.getProjectPluginPath(
            self.project, self.plugin
        )
        self.failUnless(path)
    
    def testGetApacheConfig(self):
        fsPath = self.fsPathBuilder.getProjectPluginPath(
            self.project, self.plugin
        )
        exp = 'Alias %(urlPath)s ' + fsPath 
        apacheConfig = self.plugin.getSystem().getApacheConfig(self.service)
        partOfExpected = ' %(fileSystemPath)s'
        self.assertEquals(apacheConfig, exp)

# todo: move this to kforged
from webunit import webunittest
import dm.ioc
class DeploymentTest(webunittest.WebTestCase):
    urlBuilder = kforge.url.UrlScheme()
    
    def setUp(self):
        self.setServer(self.urlBuilder.getFqdn(), 80)
        self.registry = dm.ioc.RequiredFeature('DomainRegistry')
        # use annak as guest not a member
        self.project = self.registry.projects['annakarenina']
        self.plugin = self.registry.plugins['www']
        self.project.services.create('www', plugin=self.plugin) 
        self.service = self.project.services['www']
        self.path = self.urlBuilder.getServicePath(self.service)
        if not self.path.endswith('/'):
            self.path += '/'
    
    def tearDown(self):
        self.service.delete()
        self.service.purge()
    
    def testAllowedIn(self):
        # either 403 (forbidden) or 404 depending on server but not 401 etc
        self.assertCode(self.path, [403, 404])
