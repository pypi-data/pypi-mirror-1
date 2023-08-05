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
        self.getAssertContent(
            '/project/%s/members/' % self.kuiProjectName,
            'Project Members'
        )
        self.getAssertContent(
            '/project/%s/members/' % self.kuiProjectName,
            self.kuiPersonName
        )

    def test_create(self):
        self.getAssertContent(
            '/project/%s/members/create/' % self.kuiProjectName,
            'Create member'
        )

    def test_update(self):
        self.getAssertContent(
            '/project/%s/members/%s/edit/' % (self.kuiProjectName, self.kuiPersonName),
            'Edit member'
        )

    def test_delete(self):
        self.getAssertContent(
            '/project/%s/members/%s/delete/' % (
                self.kuiProjectName, self.kuiPersonName
            ),
            'Delete member'
        )

