import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.service import ServiceListView
from kforge.django.apps.kui.views.service import ServiceCreateView
from kforge.django.apps.kui.views.service import ServiceReadView
from kforge.django.apps.kui.views.service import ServiceUpdateView
from kforge.django.apps.kui.views.service import ServiceDeleteView
import kforge.ioc

sysdict = kforge.ioc.RequiredFeature('SystemDictionary')
uri_prefix = sysdict['www.uri_prefix']

def suite():
    suites = [
        unittest.makeSuite(TestServiceListView),
        unittest.makeSuite(TestServiceCreateView),
        unittest.makeSuite(TestServiceReadView),
        unittest.makeSuite(TestServiceUpdateView),
        unittest.makeSuite(TestServiceDeleteView),
    ]
    return unittest.TestSuite(suites)


class ServiceTestCase(ViewTestCase):

    projectName = 'warandpeace'
    serviceName = 'example'

    def createViewKwds(self):
        viewKwds = super(ServiceTestCase, self).createViewKwds()
        viewKwds['domainObjectKey'] = self.projectName
        viewKwds['hasManyKey'] = self.serviceName
        return viewKwds


class TestServiceListView(ServiceTestCase):

    viewClass = ServiceListView

    def test_canCreate(self):
        object = None
        self.failIf(self.view.canCreateService())

    def test_canRead(self):
        object = None
        self.failUnless(self.view.canReadService())

    def test_canUpdate(self):
        object = None
        self.failIf(self.view.canUpdateService())

    def test_canDelete(self):
        object = None
        self.failIf(self.view.canDeleteService())


class TestServiceCreateView(ServiceTestCase):

    viewClass = ServiceCreateView
    requiredRedirect = '%s/login/' % uri_prefix
    requiredResponseClassName = 'HttpResponseRedirect'


class TestServiceReadView(ServiceTestCase):

    viewClass = ServiceReadView


class TestServiceUpdateView(ServiceTestCase):

    viewClass = ServiceUpdateView
    requiredRedirect = '%s/login/' % uri_prefix
    requiredResponseClassName = 'HttpResponseRedirect'


class TestServiceDeleteView(ServiceTestCase):

    viewClass = ServiceDeleteView
    requiredRedirect = '%s/login/' % uri_prefix
    requiredResponseClassName = 'HttpResponseRedirect'

