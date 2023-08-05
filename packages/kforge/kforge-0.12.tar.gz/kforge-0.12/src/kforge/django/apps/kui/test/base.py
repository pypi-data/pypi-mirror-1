from webunit import webunittest
import unittest
import kforge.soleInstance
import kforge.url
import random


class KuiTestCase(webunittest.WebTestCase):

    system = kforge.soleInstance.application
    kuiServer = kforge.url.UrlBuilderAdmin().getFqdn()
    kuiPort = system.dictionary['www.port_http']
    ok_code = 200

    def createNumber(self):
        return str(random.randint(1, 10000000))

    def setUp(self):
        self.setServer(self.kuiServer, self.kuiPort)
        self.kuiPersonName = 'kuitest' + self.createNumber()
        self.kuiPersonPassword = 'kuitest'
        self.kuiPersonEmail    = 'kuitest@appropriatesoftware.net'
        self.kuiPersonFullname = 'kuitestfullname'
        self.kuiProjectFullname = 'kuitestfullname'
        self.kuiProjectName = 'kuitest' + self.createNumber()
        self.kuiProjectDescription = 'kuitest project description'
        self.kuiProjectPurpose = 'kuitest project purpose'
        self.kuiProjectLicense = '1'
   
    def tearDown(self):
        pass

    def getAssertContent(self, url, content, code=ok_code):
        super(KuiTestCase, self).getAssertContent(url, content, code)

    def getAssertNotContent(self, url, content, code=ok_code):
        super(KuiTestCase, self).getAssertNotContent(url, content, code)

    def postAssertContent(self, url, params, content, code=ok_code):
        super(KuiTestCase, self).postAssertContent(url, params, content, code)

    def postAssertNotContent(self, url, params, content, code=ok_code):
        super(KuiTestCase, self).postAssertNotContent(url,params,content,code)

    def registerPerson(self):
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        params['passwordconfirmation'] = self.kuiPersonPassword
        params['fullname'] = self.kuiPersonFullname
        params['email'] = self.kuiPersonEmail
        params['emailconfirmation'] = self.kuiPersonEmail
        self.post('/person/create/', params)
        self.getAssertContent('/person/%s/' % self.kuiPersonName, self.kuiPersonName)

    def loginPerson(self):
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        self.post('/login/', params)
        requiredContent = 'Logged in'
        self.getAssertContent('/', requiredContent)

    def deletePerson(self):
        params = {}
        self.post('/person/%s/delete/' % self.kuiPersonName, params)

    def registerProject(self):
        params = {}
        params['name'] = self.kuiProjectName
        params['title'] = self.kuiProjectFullname
        params['purpose'] = self.kuiProjectPurpose
        params['licenses'] = self.kuiProjectLicense
        params['description'] = self.kuiProjectDescription
        self.post('/project/create/', params)
        requiredContent = self.kuiProjectName
        self.getAssertContent('/project/', requiredContent)
        self.getAssertContent('/project/%s/' % self.kuiProjectName, requiredContent)

    def deleteProject(self):
        location = '/project/%s/delete/' % self.kuiProjectName
        params = {}
        self.post(location, params)
        while self.kuiProjectName in self.system.registry.projects:
            project = self.system.registry.projects[self.kuiProjectName]
            project.delete()
            project.purge()
        requiredContent = self.kuiProjectName
        self.getAssertNotContent('/project/', requiredContent)

