from kforge.django.apps.kui.test.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestAdminIndex),
        unittest.makeSuite(TestListObject),
        unittest.makeSuite(TestCreateObject),
        unittest.makeSuite(TestReadObject),
        unittest.makeSuite(TestUpdateObject),
        unittest.makeSuite(TestDeleteObject),
    ]
    return unittest.TestSuite(suites)


class AdminTestCase(KuiTestCase):

    fixtureKeyName  = 'testObject'
    fixtureFullname = 'Test Object'
    fixtureType     = 'Person'
    fixtureEmail    = 'test@test.com'

    personRegister = KuiTestCase.system.registry.persons
    
    def setUp(self):
        super(AdminTestCase, self).setUp()
        while self.fixtureKeyName in self.personRegister.getAll():
            person = self.personRegister.getAll()[self.fixtureKeyName]
            person.delete()
            person.purge()
        self.registerPerson()
        self.loginPerson()
        self.visitor = self.personRegister[self.kuiPersonName]
        adminRole = self.system.registry.roles['Administrator']
        self.visitor.role = adminRole
        self.visitor.save()
        self.person_location = self.url_scheme.url_for('admin', offset='Person')
        offset = 'Person/%s/' % self.fixtureKeyName
        self.person_fxt_location = self.url_scheme.url_for('admin', offset=offset)
        
    def tearDown(self):
        while self.fixtureKeyName in self.personRegister.getAll():
            person = self.personRegister.getAll()[self.fixtureKeyName]
            person.delete()
            person.purge()
        self.deletePerson()
        self.visitor.delete()
        self.visitor.purge()
        super(AdminTestCase, self).tearDown()


class TestAdminIndex(AdminTestCase):

    def testModel(self):
        offset = self.url_scheme.url_for('admin')
        offset += '/model'
        self.getAssertContent(offset, 'Domain Model Registry')
        self.getAssertContent(offset, 'Person')

    def testClass(self):
        person_url = self.url_scheme.url_for('admin', offset='Person')
        self.getAssertContent(person_url, 'Person')
        self.getAssertContent(person_url, 'admin')
        self.getAssertContent(person_url, 'visitor')
        self.getAssertContent(person_url, self.kuiPersonName)


class TestListObject(AdminTestCase):

    def setUp(self):
        super(TestListObject, self).setUp()

    def tearDown(self):
        super(TestListObject, self).tearDown()

    def testListObject(self):
        location = self.url_scheme.url_for('admin', offset='Person')
        self.getAssertContent(location, 'admin')
        self.getAssertContent(location, 'visitor')
        

class TestCreateObject(AdminTestCase):

    fixtureKeyName  = 'TestCreateObject'
    
    def setUp(self):
        super(TestCreateObject, self).setUp()
        self.object = None

    def tearDown(self):
        super(TestCreateObject, self).tearDown()
        self.object = None

    def testCreateObject(self):
        self.failIf(self.fixtureKeyName in self.personRegister)
        self.getAssertContent(self.person_location, 'Create Person')
        self.getAssertContent(self.person_location, 'admin')
        self.getAssertNotContent(self.person_location, self.fixtureKeyName)
        location = self.url_scheme.url_for('admin', offset='create/Person/')
        self.getAssertContent(location, 'Create Person')
        params = {}
        params['name']     = self.fixtureKeyName
        params['fullname'] = self.fixtureFullname
        params['password'] = self.fixtureKeyName
        params['email']    = self.fixtureEmail
        params['role']     = 'Administrator'
        self.post(location, params)  # missing state
        params['state']    = 'active'
        self.post(location, params, code=302)
        self.failUnless(
            self.fixtureKeyName in self.personRegister,
            "'%s' not in %s" % (self.fixtureKeyName, self.personRegister.keys())
        )
        self.getAssertContent(self.person_location, self.fixtureKeyName)
 

class TestReadObject(AdminTestCase):

    def setUp(self):
        super(TestReadObject, self).setUp()

    def tearDown(self):
        super(TestReadObject, self).tearDown()

    def testReadObject(self):
        person = self.personRegister.create(self.fixtureKeyName)
        person.fullname = self.fixtureFullname
        person.save()
        location = self.person_fxt_location
        self.getAssertContent(location, self.fixtureFullname)
        self.getAssertContent(location, self.fixtureKeyName)
        

class TestUpdateObject(AdminTestCase):

    fixtureFullnameUpdated = 'Fullname Update Test'

    def setUp(self):
        super(TestUpdateObject, self).setUp()

    def tearDown(self):
        super(TestUpdateObject, self).tearDown()

    def testUpdateObject(self):
        person = self.personRegister.create(
            name     = self.fixtureKeyName,
            fullname = self.fixtureFullname,
            email    = self.fixtureEmail,
            role     = self.system.registry.roles['Visitor'],
        )
        location = self.person_fxt_location
        self.getAssertContent(location, self.fixtureKeyName)
        self.getAssertContent(location, self.fixtureFullname)
        self.getAssertNotContent(location, self.fixtureFullnameUpdated)

        offset = 'update/Person/%s/' % self.fixtureKeyName
        location = self.url_scheme.url_for('admin', offset=offset)
        self.getAssertContent(location, self.fixtureKeyName)
        self.getAssertContent(location, self.fixtureFullname)
        self.getAssertNotContent(location, self.fixtureFullnameUpdated)

        self.getAssertContent(location, 'Update Person')
        self.getAssertContent(location, self.fixtureKeyName)
        params = {}
        params['name']     = self.fixtureKeyName
        params['fullname'] = self.fixtureFullnameUpdated
        params['email']    = self.fixtureEmail
        params['role']     = 'Administrator'
        self.post(location, params, code=200)  # missing state
        params['state']    = 'active'
        self.post(location, params, code=302)

        location = self.person_fxt_location
        self.getAssertContent(location, self.fixtureFullnameUpdated)

        offset = 'update/Person/%s/' % self.fixtureKeyName
        location = self.url_scheme.url_for('admin', offset=offset)
        self.getAssertContent(location, self.fixtureFullnameUpdated)
        

class TestDeleteObject(AdminTestCase):

    def setUp(self):
        super(TestDeleteObject, self).setUp()

    def tearDown(self):
        super(TestDeleteObject, self).tearDown()

    def testDeleteObject(self):
        person = self.personRegister.create(self.fixtureKeyName)
        person.fullname = self.fixtureFullname
        person.save()
        self.getAssertContent(self.person_location, self.fixtureKeyName)
        self.getAssertContent(self.person_fxt_location, 'Delete Person')

        offset = 'delete/Person/%s/' % self.fixtureKeyName
        location = self.url_scheme.url_for('admin', offset=offset)
        self.getAssertContent(location, 'Delete Person')
        self.getAssertContent(location, self.fixtureKeyName)
        
        params = {}
        # do not need submit since that is automatically clicked
        # params['submit'] = 'submit'
        self.post(location, params)

        self.failIf(self.fixtureKeyName in self.personRegister)

