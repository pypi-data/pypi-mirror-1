import unittest
import os
from kforge.testunit import TestCase
import kforge.url

def suite():
    suites = [
            unittest.makeSuite(PluginTest),
        ]
    return unittest.TestSuite(suites)

class PluginTest(TestCase):
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not 'dav' in self.registry.plugins:
            newPlugin = self.registry.plugins.create('dav')
        self.plugin = self.registry.plugins['dav']
        self.project = self.registry.projects['annakarenina']
        if 'dav' in self.project.services:
            service = self.project.services['dav']
            service.delete()
            service.purge()
        self.project.services.create('dav', plugin=self.plugin)
        self.service = self.project.services['dav']
    
    def tearDown(self):
        if self.service != None:
            self.service.delete()
            self.service.purge()
    
    def testGetApacheConfig(self):
        apacheConfig = self.plugin.getSystem().getApacheConfig(self.service)
        urlPath = '%(urlPath)s'
        expPart = '<Location ' + urlPath + '>'
        self.failUnless(expPart in apacheConfig)

# todo: move to kforged
from webunit import webunittest
import dm.ioc
class DeploymentTest(webunittest.WebTestCase):
    urlBuilder = kforge.url.UrlScheme()
    
    def setUp(self):
        self.setServer(self.urlBuilder.getFqdn(), 80)
        self.registry = dm.ioc.RequiredFeature('DomainRegistry')
        # use warandpeace since guest a member but shouldn't be allowed to read
        self.project = self.registry.projects['warandpeace']
        self.plugin = self.registry.plugins['dav']
        self.project.services.create('dav', plugin=self.plugin)
        self.service = self.project.services['dav']
        self.path = self.urlBuilder.getServicePath(self.service)
        if not self.path.endswith('/'):
            self.path += '/'

    def tearDown(self):
        if self.service != None:
            self.service.delete()
            self.service.purge()
    
    def testNotAllowedIn(self):
        # this test will incorrectly fail due to bug
        # see trac ticket no 9 
        # self.assertCode(self.path, 401)
        pass
    
    def testAllowedIn(self):
        # should have +Indexes so 400 not 404
        self.setBasicAuth('natasha', 'natasha')
        self.assertCode(self.path, 200)
