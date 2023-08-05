from kforge.django.apps.kui.test.admin.domainObject import AdminTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestHasManyAttribute),
    ]
    return unittest.TestSuite(suites)


class TestHasManyAttribute(AdminTestCase):

    def setUp(self):
        super(TestHasManyAttribute, self).setUp()

    def tearDown(self):
        super(TestHasManyAttribute, self).tearDown()

    def testMemberList(self):
        self.getAssertContent(
            '/admin/model/Project/administration/members/',
            'admin'
        )

    def testMemberCreate(self):
        self.getAssertContent(
            '/admin/model/create/Project/administration/members/',
            'Create Member'
        )

    def testMemberRead(self):
        self.getAssertContent(
            '/admin/model/Project/administration/members/admin/',
            'admin'
        )

    def testMemberUpdate(self):
        self.getAssertContent(
            '/admin/model/update/Project/administration/members/admin/',
            'Update Member'
        )

    def testMemberDelete(self):
        self.getAssertContent(
            '/admin/model/delete/Project/administration/members/admin/',
            'Delete Member'
        )

