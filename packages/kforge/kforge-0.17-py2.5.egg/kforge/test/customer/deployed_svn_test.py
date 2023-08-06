import unittest
from webunit import webunittest
import tempfile
import os

import kforge.url
import kforge.utils
# set up dom to have some projects, people and services
# build it all clean incl. apache so we don't have to worry what has been
# done elsewhere 
import kforge.test.domain_setup
import kforge.plugin.apacheconfig
configBuilder = kforge.apache.apacheconfig.ApacheConfigBuilder()
configBuilder.buildConfig()
configBuilder.reloadConfig()

def suite():
    suites = [
        unittest.makeSuite(DeployedSvnTest),
        ]
    return unittest.TestSuite(suites)


class DeployedSvnTest(webunittest.WebTestCase):
    def setUp(self):
        self.urlBuilder = kforge.url.UrlBuilderProject()
        self.fqdn = self.urlBuilder.getFqdn()
        self.setServer(self.fqdn, 80)
        # need trailing slashor you get 301 (redirect) which messes up tests
        self.urlPath = '/annakarenina/svn/svn/'
        self.name = 'levin'
        self.password = 'levin'
    
    def testCannotAccessPrivate(self):
        # make sure we need authorization
        self.assertCode(self.urlPath, 401)
    
    def testAuthentication(self):
        self.setBasicAuth(self.name, self.password)
        self.assertCode(self.urlPath, 200)
    
    def testCheckout(self):
        basedir = tempfile.mkdtemp(prefix='svn-checkout')
        url = 'http://' + self.fqdn  + self.urlPath
        cmd = 'svn co --username %s --password %s %s ./' % ( self.name,
                                                          self.password,
                                                          url)
        os.chdir(basedir)
        if os.system(cmd):
            self.fail('Failed to checkout')
        fileName = 'xyz.txt'
        ff = file(fileName, 'w')
        ff.write('hello world')
        ff.close()
        cmd2 = 'svn add %s' % fileName
        cmd3 = 'svn ci %s -m "x"' % fileName
        os.system(cmd2)
        if os.system(cmd3):
            self.fail('Failed to checkin')
