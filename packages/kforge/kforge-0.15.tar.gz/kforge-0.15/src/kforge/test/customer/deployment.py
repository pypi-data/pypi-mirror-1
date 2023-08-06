import unittest

from dm.ioc import *
import kforge.apache.apacheconfig

# deployment tests
import kforge.apachetest
import kforge.test.deployed_site_test
import kforge.django.apps.kui.test
import kforge.plugin.davtest
import kforge.plugin.wwwtest

registry = RequiredFeature('DomainRegistry')
if not registry.plugins.has_key('www'):
    newPlugin = registry.plugins.create('www')
if not registry.plugins.has_key('dav'):
    newPlugin = registry.plugins.create('dav')

kforge.apache.apacheconfig.ApacheConfigBuilder().buildConfig()
# reloading of web server will be done in kforge.apache.apacheconfigtest

def suite():
    suites = [
            kforge.apachetest.suite(),
            kforge.test.deployed_site_test.suite(),
            # kforge.django.apps.kui.test.suite(),
            # [[TODO: temporarily commented out as broken due to removal of domain_setup]]
            unittest.makeSuite(kforge.plugin.wwwtest.DeploymentTest),
            unittest.makeSuite(kforge.plugin.davtest.DeploymentTest),
        ]
    return unittest.TestSuite(suites)
