from kforge.django.apps.kui.test.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestReadPersons),
        unittest.makeSuite(TestPersonCRUD),
    ]
    return unittest.TestSuite(suites)

class TestReadPersons(KuiTestCase):

    personName = 'admin'
   
    def testPersonIndex(self):
        offset = self.url_scheme.url_for('person')
        self.getAssertContent(offset, [
            'Registered people',
            'There are %s registered people' % self.registry.persons.count()
        ])

    def testPersonSearch(self):
        params = {'userQuery': 'z'}
        offset = self.url_scheme.url_for('person', action='search', id=None)
        self.postAssertNotContent(offset, params, self.personName)
        params = {'userQuery': 'a'}
        self.postAssertContent(offset, params, self.personName)
    
    def testPersonSearch(self):
        offset = self.url_scheme.url_for('person', action='find', id='z')
        self.getAssertNotContent(offset, self.personName)
        offset = self.url_scheme.url_for('person', action='find', id='a')
        self.getAssertContent(offset, self.personName)

    def testPersonRead(self):
        testLocation = self.url_scheme.url_for('person', action='read',
                id=self.personName)
        requiredContent = 'This is the profile page for'
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = self.personName
        self.getAssertContent(testLocation, requiredContent)

    def testPersonCreate(self):
        offset = self.url_scheme.url_for('person', action='create')
        self.getAssertContent(offset, 'Register a new user')


class TestPersonCRUD(KuiTestCase):

    def testCRUD(self):
        self.kuiPersonName = 'kuitest' + self.createNumber()
        self.kuiPassword = 'kuitest'
        self.kuiEmail    = 'kuitest@appropriatesoftware.net'
        self.kuiFullname = 'kuitestfullname'

        # create
        requiredContent = 'Register a new user'
        path = self.url_scheme.url_for('person', action='create')
        self.getAssertContent(path, requiredContent)
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        params['passwordconfirmation'] = self.kuiPersonPassword
        params['fullname'] = self.kuiPersonFullname
        params['email'] = self.kuiPersonEmail
        params['emailconfirmation'] = self.kuiPersonEmail
        self.post(path, params)

        # read
        requiredContent = 'profile page for'
        read_path = self.url_scheme.url_for('person', action='read',
                id=self.kuiPersonName)
        self.getAssertContent(read_path, requiredContent)
        requiredContent = self.kuiFullname
        self.getAssertContent(read_path, requiredContent)
        requiredContent = self.kuiPersonName
        self.getAssertContent(read_path, requiredContent)
        self._login(self.kuiPersonName, self.kuiPersonPassword)
        home_path = self.url_scheme.url_for('home')
        self.getAssertContent(home_path, requiredContent)
        path = self.url_scheme.url_for('person', action='home')
        self.getAssertContent(path, self.kuiPersonEmail)
        
        # update
        requiredContent = 'Edit your profile'
        path = self.url_scheme.url_for('person', action='edit',
                id=self.kuiPersonName)
        self.getAssertContent(path, requiredContent)
        self.getAssertContent(path, self.kuiPersonName)
        self.getAssertContent(path, self.kuiPersonFullname)
        params = {}
        params['submission'] = '1'
        params['password'] = ''
        params['passwordconfirmation'] = ''
        kuiFullnameCorrection = 'newCorrectFullname'
        params['fullname'] = kuiFullnameCorrection
        params['email'] = self.kuiPersonEmail
        self.post(path, params)
        read_path =  self.url_scheme.url_for('person', action='read',
                id=self.kuiPersonName)
        self.getAssertContent(read_path, self.kuiPersonName)
        self.getAssertContent(read_path, kuiFullnameCorrection)
        
        # delete
        params = {}
        delete_path = self.url_scheme.url_for('person', action='delete',
                id=self.kuiPersonName)
        self.post(delete_path, params)
        requiredContent = 'Register'
        self.getAssertContent(home_path, requiredContent)
        requiredContent = 'Logged in'
        self.getAssertNotContent(home_path, requiredContent)

