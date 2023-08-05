import kforge.url
import unittest
from kforge.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(UrlBuilderBaseTest),
        unittest.makeSuite(UrlBuilderTest),
    ]
    return unittest.TestSuite(suites)

class UrlBuilderBaseTest(TestCase):

    def testMakeUrlPath(self):
        components = ['a', 'b', 'c']
        scheme = kforge.url.UrlBuilderBase()
        out = scheme.makeUrlPath(components)
        expected = '/a/b/c'
        self.assertEqual(out, expected)


class UrlBuilderTest(TestCase):
   
    def setUp(self):
        super(UrlBuilderTest, self).setUp()
        self.project = self.registry.projects['example']
        self.plugin = self.registry.plugins['example']
        self.service = self.project.services['example']
        self.singleServicePlugin = self.registry.plugins['example_single_service']
        self.singleService = self.project.services['example_single_service']
    
        self.builderAdmin = kforge.url.UrlBuilderAdmin()
        self.builderProject = kforge.url.UrlBuilderProject()
        self.schemes = [self.builderAdmin, self.builderProject]
    
    def testGetFqdn(self):
        for scheme in self.schemes:
            fqdn = scheme.getFqdn()
            self.failUnless(scheme.getTypeCode() in fqdn)
    
    def testGetWebRoot(self):
        for scheme in self.schemes:
            webroot = scheme.getWebRoot()
            self.failUnless(scheme.getTypeCode() in webroot)
    
    def testGetProjectPath(self):
        for scheme in self.schemes:
            path = scheme.getProjectPath(self.project)
            self.failUnless(self.project.name in path)
    
    def testGetServicePath(self):
        scheme = self.builderProject
        path = scheme.getServicePath(self.service)
        self.failUnless('/' in path)
        exp = '/%s/%s' % ( self.project.name, self.service.name)
        self.assertEquals(exp, path, '%s not in %s' % (exp, path))
        # exp = '/' + self.project.name + '/' + self.singleServicePlugin.name
        # out = self.builderProject.getServicePath(self.singleService)
        # self.assertEquals(out, exp)
    
    def testGetServiceUrl(self):
        for scheme in self.schemes:
            url = scheme.getServiceUrl(self.service)
            exp = 'http://' + scheme.getFqdn()
            if self.dictionary['www.port_http'] != '80':
                exp += ":" + self.dictionary['www.port_http']
            exp += scheme.getServicePath(self.service)
            self.assertEquals(exp, url)

