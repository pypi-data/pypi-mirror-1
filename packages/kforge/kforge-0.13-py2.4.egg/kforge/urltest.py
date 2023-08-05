import kforge.url
import unittest
from kforge.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(UrlSchemeTest),
        unittest.makeSuite(UrlSchemeUriPrefixTest),
    ]
    return unittest.TestSuite(suites)

class UrlSchemeTest(TestCase):
    prefix = ''

    def setUp(self):
        self.dictionary = kforge.ioc.RequiredFeature('SystemDictionary')
        self.current_prefix = self.dictionary['www.uri_prefix']
        self.dictionary.set('www.uri_prefix', self.prefix)
        self.scheme = kforge.url.UrlScheme()

    def tearDown(self):
        self.dictionary.set('www.uri_prefix', self.current_prefix)

    def _path(self, path):
        return self.prefix + path

    def testBase(self):
        out = self.scheme.url_for('home')
        assert out == self._path('/')

    def testMedia(self):
        out = self.scheme.url_for('media')
        assert out == self._path('/media')
        out = self.scheme.url_for('media', offset='/css/master.css')
        assert out == self._path('/media/css/master.css')
        out = self.scheme.url_for_qualified('media', offset='/css/master.css')
        exp = self._path('/media/css/master.css')
        assert exp in out

    def testPerson(self):
        out = self.scheme.url_for('person')
        assert out == self._path('/person')
        out = self.scheme.url_for('person', action='home')
        assert out == self._path('/person/home')
        out = self.scheme.url_for('person', action='create')
        assert out == self._path('/person/create')
        out = self.scheme.url_for('person', action='read', id=9)
        assert out == self._path('/person/9')
        out = self.scheme.url_for('person', action='delete', id=9)
        assert out == self._path('/person/9/delete')

    def testProject(self):
        out = self.scheme.url_for('project')
        assert out == self._path('/project')
        out = self.scheme.url_for('project', action='search')
        assert out == self._path('/project/search')
        out = self.scheme.url_for('project', action='read', id='annakarenina')
        assert out == self._path('/project/annakarenina')

    def test_ProjectAdmin(self):
        out = self.scheme.url_for('project.admin', project='annakarenina',
                subcontroller='services', action='read', id=3)
        assert out == self._path('/project/annakarenina/services/3')
        out = self.scheme.url_for('project.admin', project='annakarenina',
                subcontroller='services', action='create')
        assert out == self._path('/project/annakarenina/services/create')

    def test_ProjectService(self):
        out = self.scheme.url_for('project.service', project='annakarenina',
                service='wiki')
        assert out == self._path('/annakarenina/wiki')

    def test_admin(self):
        out = self.scheme.url_for('admin')
        assert out == self._path('/admin/model')
        out = self.scheme.url_for('admin', offset='Project/read/2')
        assert out == self._path('/admin/model/Project/read/2')

    def test_decodeServicePath(self):
        inpath = self._path(u'/annakarenina/wiki')
        out_project, out_service = self.scheme.decodeServicePath(inpath)
        assert out_project == 'annakarenina'
        assert out_service == 'wiki'
        assert type(out_project) == str 

    def test_decodeServicePath_2(self):
        inpath = self._path('/warandpeace/svn/!svn/vcc/default')
        out_project, out_service = self.scheme.decodeServicePath(inpath)
        assert out_project == 'warandpeace'
        assert out_service == 'svn'

    def test_getServicePath(self):
        project_name = 'a_really_weird_name'
        class ProjectStub:
            name = project_name

        class ServiceStub:
            project = ProjectStub()
            name = 'service_stub'

        out = self.scheme.getServicePath(ServiceStub())
        assert out == self._path('/%s/service_stub' % project_name)

    def test_getServiceUrl(self):
        project_name = 'a_really_weird_name'
        class ProjectStub:
            name = project_name
        class ServiceStub:
            project = ProjectStub()
            name = 'service_stub'

        out = self.scheme.getServiceUrl(ServiceStub())
        exp = self._path('/%s/service_stub' % project_name)
        assert out.endswith(exp)


class UrlSchemeUriPrefixTest(UrlSchemeTest):
    prefix = '/myrandomprefix'

