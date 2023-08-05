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
        while self.fixtureKeyName in self.personRegister.all:
            person = self.personRegister.all[self.fixtureKeyName]
            person.delete()
            person.purge()
        self.registerPerson()
        self.loginPerson()
        self.visitor = self.personRegister[self.kuiPersonName]
        adminRole = self.system.registry.roles['Administrator']
        self.visitor.role = adminRole
        self.visitor.save()
        
    def tearDown(self):
        while self.fixtureKeyName in self.personRegister.all:
            person = self.personRegister.all[self.fixtureKeyName]
            person.delete()
            person.purge()
        self.deletePerson()
        self.visitor.delete()
        self.visitor.purge()
        super(AdminTestCase, self).tearDown()


class TestAdminIndex(AdminTestCase):

    def testIndex(self):
        self.getAssertContent('/admin/', 'Welcome')
        self.getAssertContent('/admin/', 'Model')

    def testModel(self):
        self.getAssertContent('/admin/model/', 'Domain Model Registry')
        self.getAssertContent('/admin/model/', 'Person')

    def testClass(self):
        self.getAssertContent('/admin/model/Person/', 'Person')
        self.getAssertContent('/admin/model/Person/', 'admin')
        self.getAssertContent('/admin/model/Person/', 'visitor')
        self.getAssertContent('/admin/model/Person/', self.kuiPersonName)


class TestListObject(AdminTestCase):

    def setUp(self):
        super(TestListObject, self).setUp()

    def tearDown(self):
        super(TestListObject, self).tearDown()

    def testListObject(self):
        location = '/admin/model/Person/'
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
        location = '/admin/model/Person/'
        self.getAssertContent(location, 'Create Person')
        self.getAssertContent(location, 'admin')
        self.getAssertNotContent(location, self.fixtureKeyName)
        location = '/admin/model/create/Person/'
        self.getAssertContent(location, 'Create Person')
        params = {}
        params['name']     = self.fixtureKeyName
        params['fullname'] = self.fixtureFullname
        params['password'] = self.fixtureKeyName
        params['email']    = self.fixtureEmail
        params['role']     = 'Administrator'
        self.post(location, params, code=[200])  # missing state
        params['state']    = 'active'
        self.post(location, params, code=[302])
        self.failUnless(
            self.fixtureKeyName in self.personRegister,
            "'%s' not in %s" % (self.fixtureKeyName, self.personRegister.keys())
        )
        location = '/admin/model/Person/'
        self.getAssertContent(location, self.fixtureKeyName)
 

class TestReadObject(AdminTestCase):

    def setUp(self):
        super(TestReadObject, self).setUp()

    def tearDown(self):
        super(TestReadObject, self).tearDown()

    def testReadObject(self):
        person = self.personRegister.create(self.fixtureKeyName)
        person.fullname = self.fixtureFullname
        person.save()
        location = '/admin/model/Person/%s/' % self.fixtureKeyName
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
        location = '/admin/model/Person/%s/' % self.fixtureKeyName
        self.getAssertContent(location, self.fixtureKeyName)
        self.getAssertContent(location, self.fixtureFullname)
        self.getAssertNotContent(location, self.fixtureFullnameUpdated)
        location = '/admin/model/update/Person/%s/' % self.fixtureKeyName
        self.getAssertContent(location, self.fixtureKeyName)
        self.getAssertContent(location, self.fixtureFullname)
        self.getAssertNotContent(location, self.fixtureFullnameUpdated)
        location = '/admin/model/update/Person/%s/' % self.fixtureKeyName
        self.getAssertContent(location, 'Update Person')
        self.getAssertContent(location, self.fixtureKeyName)
        params = {}
        params['name']     = self.fixtureKeyName
        params['fullname'] = self.fixtureFullnameUpdated
        params['email']    = self.fixtureEmail
        params['role']     = 'Administrator'
        self.post(location, params, code=[200])  # missing state
        params['state']    = 'active'
        self.post(location, params, code=[302])
        location = '/admin/model/Person/%s/' % self.fixtureKeyName
        self.getAssertContent(location, self.fixtureFullnameUpdated)
        location = '/admin/model/update/Person/%s/' % self.fixtureKeyName
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
        location = '/admin/model/Person/'
        self.getAssertContent(location, self.fixtureKeyName)
        location = '/admin/model/Person/%s/' % self.fixtureKeyName
        self.getAssertContent(location, 'Delete Person')
        location = '/admin/model/delete/Person/%s/' % self.fixtureKeyName
        self.getAssertContent(location, 'Delete Person')
        self.getAssertContent(location, self.fixtureKeyName)
        
        params = {}
        params['submit'] = 'submit'
        self.post(location, params)

        self.failIf(self.fixtureKeyName in self.personRegister)

