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
        offset = self.url_scheme.url_for('project.admin',
                project=self.kuiProjectName, subcontroller='services')
        self.getAssertContent(
            offset,
            'Project Services'
        )

