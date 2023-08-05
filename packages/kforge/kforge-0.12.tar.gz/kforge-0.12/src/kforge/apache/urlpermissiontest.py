from kforge.testunit import TestCase
import unittest
import kforge.apache.urlpermission as urlpermission

def suite():
    suites = [
        unittest.makeSuite(ParseUrlTest),
    ]
    return unittest.TestSuite(suites)

class ParseUrlTest(TestCase):
    
    def setUp(self):
        self.urlPath = '/annakarenina/example'
        self.hostPath = 'project.local.kforge.net'
    
    def testGetVisitorName(self):
        visitorName = 'visitor'
        outName = urlpermission.getVisitorName('notauser', 'asdfghjkl')
        self.failUnless(outName == visitorName)
        outName = urlpermission.getVisitorName('levin', 'levin')
        self.failUnless(outName == 'levin')
    
    def testGetService(self):
        service = urlpermission.getService(self.urlPath)
        self.failUnless(service.name == 'example')
    
    def testGetActionName(self):
        httpMethods = [ ('GET',      'Read'),
                        ('PROPFIND', 'Read'),
                        ('OPTIONS',  'Read'),
                        ('REPORT',   'Read'),
                        ('POST',     'Update'),
                      ]
        for httpMethod in httpMethods:
            actionName = urlpermission.getActionName(httpMethod[0])
            self.failUnless(actionName == httpMethod[1],
                'Failed with http method: %s' % httpMethod[0])
    
    def testIsAllowedAccess(self):
        out = urlpermission.isAllowedAccess('levin', self.urlPath, 'GET')
        self.failUnless(out)
        out = urlpermission.isAllowedAccess('natasha', self.urlPath, 'GET')
        self.failIf(out)
    
    def test_isAllowedAccess2(self):
        "warandpeace allows visitor access"
        urlpath = '/warandpeace/example'
        out = urlpermission.isAllowedAccess('natasha', urlpath, 'GET')
        self.failUnless(out, 'natasha not allowed in')
        out = urlpermission.isAllowedAccess('visitor', urlpath, 'GET')
        self.failUnless(out, 'visitor not allowed in')
        out = urlpermission.isAllowedAccess('levin', urlpath, 'GET')
        self.failUnless(out, 'levin not allowed in')

