from kforge.django.apps.kui.test.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestReadProjects),
        unittest.makeSuite(TestProjectCRUD),
    ]
    return unittest.TestSuite(suites)


class TestReadProjects(KuiTestCase):
  
    projectName = 'administration'
  
    def testProjectIndex(self):
        self.getAssertContent('/project/', 'Registered projects')
        self.getAssertContent('/project/search/', 'Search projects')

    def testProjectSearch(self):
        params = {'userQuery': 'z'}
        self.postAssertNotContent('/project/search/', params, self.projectName)
        params = {'userQuery': 'a'}
        self.postAssertContent('/project/search/', params, self.projectName)
        
    def testProjectRead(self):
        self.getAssertContent(
            '/project/%s/' % self.projectName,
            'Short name:'
        )
        self.getAssertContent(
            '/project/%s/' % self.projectName,
            self.projectName
        )
        
    def testMembersRead(self):
        self.getAssertContent(
            '/project/%s/members/' % self.projectName, 
            'Here are all the members'
        )
        self.getAssertContent(
            '/project/%s/members/' % self.projectName, 
            self.projectName
        )
        self.getAssertContent(
            '/project/%s/members/' % self.projectName, 
            'Administrator'
        )
        self.getAssertContent(
            '/project/%s/members/' % self.projectName, 
            'Visitor'
        )
        
    def testServicesRead(self):
        self.getAssertContent(
            '/project/%s/services/' % self.projectName, 
            self.projectName
        )


class TestProjectCRUD(KuiTestCase):

    def setUp(self):
        super(TestProjectCRUD, self).setUp()
        self.registerPerson()
        self.loginPerson()

    def tearDown(self):
        self.deletePerson()
        if self.kuiProjectName in self.system.registry.projects:
            project = self.system.registry.projects[self.kuiProjectName]
            project.delete()
            project.purge()


    def testCRUD(self):
        # Create
        self.failIf(self.kuiProjectName in self.system.registry.projects)
        requiredContent = 'Register a new project'
        self.getAssertContent('/project/create/', requiredContent)
        requiredContent = 'Please enter the details of your new project below'
        self.getAssertContent('/project/create/', requiredContent)
        params = {}
        params['title'] = self.kuiProjectFullname
        params['purpose'] = self.kuiProjectPurpose
        params['licenses'] = self.kuiProjectLicense
        params['description'] = self.kuiProjectDescription
        params['name'] = self.kuiProjectName
        self.post('/project/create/', params)
        self.failUnless(self.kuiProjectName in self.system.registry.projects)
        project = self.system.registry.projects[self.kuiProjectName]
        person = self.system.registry.persons[self.kuiPersonName]
        self.failUnless(person in project.members)
        membership = project.members[person]
        self.failUnlessEqual(membership.role.name, 'Administrator')

        # Read
        self.failUnless(self.kuiProjectName in self.system.registry.projects)
        testLocation = '/project/%s/' % self.kuiProjectName
        requiredContent = 'Edit'
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = 'Delete'
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = '%s' % self.kuiProjectName
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = '%s' % self.kuiProjectDescription
        self.getAssertContent(testLocation, requiredContent)
        requiredContent = '%s' % self.kuiProjectFullname
        self.getAssertContent(testLocation, requiredContent)
        
        # Update
        self.failUnless(self.kuiProjectName in self.system.registry.projects)
        requiredContent = 'Edit project' 
        self.getAssertContent('/project/%s/edit/' % self.kuiProjectName, requiredContent)
        self.getAssertContent('/project/%s/edit/' % self.kuiProjectName, self.kuiProjectName)
        self.getAssertContent('/project/%s/edit/' % self.kuiProjectName, self.kuiProjectFullname)
        self.getAssertContent('/project/%s/edit/' % self.kuiProjectName, self.kuiProjectDescription)

        # Delete
        self.failUnless(self.kuiProjectName in self.system.registry.projects)
        params = {}
        params['submit'] = 'submit'
        self.post('/project/%s/delete/' % self.kuiProjectName, params)
        self.failIf(self.kuiProjectName in self.system.registry.projects)

