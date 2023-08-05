from kforge.django.apps.kui.test.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestServiceCRUD),
    ]
    return unittest.TestSuite(suites)


class TestServiceCRUD(KuiTestCase):

    def setUp(self):
        super(TestServiceCRUD, self).setUp()
        self.registerPerson()
        self.loginPerson()
        self.registerProject()

    def tearDown(self):
        super(TestServiceCRUD, self).tearDown()
        self.deleteProject()
        self.deletePerson()

    def test_service_list(self):
        self.getAssertContent(
            '/project/%s/services/' % self.kuiProjectName,
            'Project Services'
        )

    def __test_service_create(self):
        self.getAssertContent(
            '/project/warandpeace/services/create/',
            'Create service'
        )

    def test_service_read(self):
        self.getAssertContent(
            '/project/warandpeace/services/example/',
            'Service: example'
        )

    def __test_service_update(self):
        self.getAssertContent(
            '/project/warandpeace/services/example/edit/',
            'Edit service: example'
        )

    def __test_service_delete(self):
        self.getAssertContent(
            '/project/warandpeace/services/example/delete/',
            'Delete service: example'
        )

