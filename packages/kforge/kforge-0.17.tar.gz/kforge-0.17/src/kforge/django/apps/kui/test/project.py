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
    index_path = KuiTestCase.url_scheme.url_for('project', action='index')
    read_path = KuiTestCase.url_scheme.url_for('project', action='read',
            id=projectName)
    create_path = KuiTestCase.url_scheme.url_for('project', action='create')
    delete_path = KuiTestCase.url_scheme.url_for('project', action='delete',
            id=projectName)
    edit_path = KuiTestCase.url_scheme.url_for('project', action='delete',
            id=projectName)
    search_path = KuiTestCase.url_scheme.url_for('project', action='search',
            id=None)

  
    def testProjectIndex(self):
        self.getAssertContent(self.index_path, 'Registered projects')
        self.getAssertContent(self.search_path, 'Search projects')

    def testProjectSearch(self):
        params = {'userQuery': 'z'}
        self.postAssertNotContent(self.search_path, params, self.projectName)
        params = {'userQuery': 'a'}
        self.postAssertContent(self.search_path, params, self.projectName)
        
    def testProjectRead(self):
        self.getAssertContent(
            self.read_path,
            'Short name:'
        )
        self.getAssertContent(
            self.read_path,
            self.projectName
        )
        
    def testMembersRead(self):
        offset = self.url_scheme.url_for('project.admin',
                project=self.projectName, subcontroller='members')
        self.getAssertContent(
            offset,
            'Here are all the members'
        )
        self.getAssertContent(
            offset,
            self.projectName
        )
        self.getAssertContent(
            offset,
            'Administrator'
        )
        self.getAssertContent(
            offset,
            'Visitor'
        )
        
    def testServicesRead(self):
        offset = self.url_scheme.url_for('project.admin',
                project=self.projectName, subcontroller='services')
        self.getAssertContent(
            offset,
            self.projectName
        )


class TestProjectCRUD(KuiTestCase):


    def setUp(self):
        super(TestProjectCRUD, self).setUp()
        self.registerPerson()
        self.loginPerson()
        self.read_path = KuiTestCase.url_scheme.url_for('project', action='read',
                id=self.kuiProjectName)
        self.create_path = KuiTestCase.url_scheme.url_for('project', action='create')
        self.delete_path = KuiTestCase.url_scheme.url_for('project', action='delete',
                id=self.kuiProjectName)
        self.edit_path = KuiTestCase.url_scheme.url_for('project', action='edit',
                id=self.kuiProjectName)


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
        self.getAssertContent(self.create_path, requiredContent)
        requiredContent = 'Please enter the details of your new project below'
        self.getAssertContent(self.create_path, requiredContent)
        params = {}
        params['title'] = self.kuiProjectFullname
        params['licenses'] = self.kuiProjectLicense
        params['description'] = self.kuiProjectDescription
        params['name'] = self.kuiProjectName
        self.post(self.create_path, params)
        self.failUnless(self.kuiProjectName in self.system.registry.projects)
        project = self.system.registry.projects[self.kuiProjectName]
        person = self.system.registry.persons[self.kuiPersonName]
        self.failUnless(person in project.members)
        membership = project.members[person]
        self.failUnlessEqual(membership.role.name, 'Administrator')

        # Read
        self.failUnless(self.kuiProjectName in self.system.registry.projects)
        requiredContent = 'Edit'
        self.getAssertContent(self.read_path, requiredContent)
        requiredContent = 'Delete'
        self.getAssertContent(self.read_path, requiredContent)
        requiredContent = '%s' % self.kuiProjectName
        self.getAssertContent(self.read_path, requiredContent)
        requiredContent = '%s' % self.kuiProjectDescription
        self.getAssertContent(self.read_path, requiredContent)
        requiredContent = '%s' % self.kuiProjectFullname
        self.getAssertContent(self.read_path, requiredContent)
        
        # Update
        self.failUnless(self.kuiProjectName in self.system.registry.projects)
        requiredContent = 'Edit project' 
        self.getAssertContent(self.edit_path, requiredContent)
        self.getAssertContent(self.edit_path, self.kuiProjectName)
        self.getAssertContent(self.edit_path, self.kuiProjectFullname)
        self.getAssertContent(self.edit_path, self.kuiProjectDescription)

        # Delete
        self.failUnless(self.kuiProjectName in self.system.registry.projects)
        params = {}
        self.post(self.delete_path, params)
        self.failIf(self.kuiProjectName in self.system.registry.projects)

