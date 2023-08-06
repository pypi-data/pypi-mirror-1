from kforge.django.apps.kui.test.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestMemberCRUD),
    ]
    return unittest.TestSuite(suites)


class TestMemberCRUD(KuiTestCase):

    def setUp(self):
        super(TestMemberCRUD, self).setUp()
        self.registerPerson()
        self.loginPerson()
        self.registerProject()

    def tearDown(self):
        super(TestMemberCRUD, self).tearDown()
        self.deleteProject()
        self.deletePerson()

    def test_list(self):
        offset = self.url_scheme.url_for('project.admin',
                project=self.kuiProjectName, subcontroller='members')
        self.getAssertContent(
            offset,
            'Project Members'
        )
        self.getAssertContent(
            offset,
            self.kuiPersonName
        )

    def test_create(self):
        offset = self.url_scheme.url_for('project.admin',
                project=self.kuiProjectName, subcontroller='members',
                action='create')
        self.getAssertContent(
            offset,
            'Create member'
        )

    def test_update(self):
        offset = self.url_scheme.url_for('project.admin',
                project=self.kuiProjectName, subcontroller='members',
                action='edit', id=self.kuiPersonName)
        self.getAssertContent(
            offset,
            'Edit member'
        )

    def test_delete(self):
        offset = self.url_scheme.url_for('project.admin',
                project=self.kuiProjectName, subcontroller='members',
                action='delete', id=self.kuiPersonName)
        self.getAssertContent(
            offset,
            'Delete member'
        )

