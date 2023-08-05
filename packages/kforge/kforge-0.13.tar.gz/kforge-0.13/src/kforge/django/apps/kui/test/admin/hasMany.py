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
        location = self.url_scheme.url_for('admin',
                offset='Project/administration/members/')
        self.getAssertContent(
            location,
            'admin'
        )

    def testMemberCreate(self):
        location = self.url_scheme.url_for('admin',
                offset='create/Project/administration/members/')
        self.getAssertContent(
            location, 
            'Create Member'
        )

    def testMemberRead(self):
        location = self.url_scheme.url_for('admin',
                offset='create/Project/administration/members/admin/')
        self.getAssertContent(
            location,
            'admin'
        )

    def testMemberUpdate(self):
        location = self.url_scheme.url_for('admin',
                offset='update/Project/administration/members/admin/')
        self.getAssertContent(
            location, 
            'Update Member'
        )

    def testMemberDelete(self):
        location = self.url_scheme.url_for('admin',
                offset='delete/Project/administration/members/admin/')
        self.getAssertContent(
            location, 
            'Delete Member'
        )

