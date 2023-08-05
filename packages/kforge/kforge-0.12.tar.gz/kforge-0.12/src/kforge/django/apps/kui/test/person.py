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
        self.getAssertContent('/person/', 'Registered people')

    def testPersonSearch(self):
        params = {'userQuery': 'z'}
        self.postAssertNotContent('/person/search/', params, self.personName)
        params = {'userQuery': 'a'}
        self.postAssertContent('/person/search/', params, self.personName)
    
    def testPersonSearch(self):
        self.getAssertNotContent('/person/find/z/', self.personName)
        self.getAssertContent('/person/find/a/', self.personName)

    def testPersonRead(self):
        testLocation = '/person/%s/' % self.personName
        requiredContent = 'This is the profile page for'
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = self.personName
        self.getAssertContent(testLocation, requiredContent)

    def testPersonCreate(self):
        self.getAssertContent('/person/create/', 'Register a new user')


class TestPersonCRUD(KuiTestCase):

    def testCRUD(self):
        self.kuiPersonName = 'kuitest' + self.createNumber()
        self.kuiPassword = 'kuitest'
        self.kuiEmail    = 'kuitest@appropriatesoftware.net'
        self.kuiFullname = 'kuitestfullname'

        # create
        requiredContent = 'Register a new user'
        self.getAssertContent('/person/create/', requiredContent)
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        params['passwordconfirmation'] = self.kuiPersonPassword
        params['fullname'] = self.kuiPersonFullname
        params['email'] = self.kuiPersonEmail
        params['emailconfirmation'] = self.kuiPersonEmail
        self.post('/person/create/', params)
        requiredContent = 'profile page for'
        location = '/person/%s/' % self.kuiPersonName
        self.getAssertContent(location, requiredContent)
        requiredContent = self.kuiFullname
        self.getAssertContent(location, requiredContent)
        
        # read
        testLocation = '/person/%s/' % self.kuiPersonName
        requiredContent = 'profile page for'
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = self.kuiPersonName
        self.getAssertContent(testLocation, requiredContent)
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        self.post('/login/', params)
        requiredContent = 'Logged in'
        self.getAssertContent('/', requiredContent)
        self.getAssertContent('/person/home/', self.kuiPersonEmail)
        
        # update
        requiredContent = 'Edit your profile'
        self.getAssertContent('/person/%s/edit/' % self.kuiPersonName, requiredContent)
        self.getAssertContent('/person/%s/edit/' % self.kuiPersonName, self.kuiPersonName)
        self.getAssertContent('/person/%s/edit/' % self.kuiPersonName, self.kuiPersonFullname)
        params = {}
        params['submission'] = '1'
        params['password'] = ''
        params['passwordconfirmation'] = ''
        kuiFullnameCorrection = 'newCorrectFullname'
        params['fullname'] = kuiFullnameCorrection
        params['email'] = self.kuiPersonEmail
        params['emailconfirmation'] = self.kuiPersonEmail
        self.post('/person/%s/edit/' % self.kuiPersonName, params)
        self.getAssertContent('/person/%s/' % self.kuiPersonName, self.kuiPersonName)
        self.getAssertContent('/person/%s/' % self.kuiPersonName, kuiFullnameCorrection)
        
        # delete
        params = {'submit': 'Delete'}
        self.post('/person/%s/delete/' % self.kuiPersonName, params)
        requiredContent = 'Register'
        self.getAssertContent('/', requiredContent)
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        self.post('/login/', params)
        requiredContent = 'Logged in'
        self.getAssertNotContent('/', requiredContent)

