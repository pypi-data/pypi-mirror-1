"""
To run tests:
    (a) run UpgradeTest
    (b) run bin/kforge-test (note that if you aren't running in development
    mode you will need to run createDevelopmentData first)
"""
import os
import unittest
import kforge.utils.upgrade
import kforge.utils.admin

class UpgradeDataTo0Point11Test(unittest.TestCase):
    
    def setUp(self):
        self.tmpDir = tempfile.mkdtemp()
        self.cmd = kforge.utils.admin.InitialiseFilesystem(self.tmpDir)
        self.cmd.execute()
        self.upgradeCmd = UpgradeEnvCmd(self.tmpDir)
        self.upgradeCmd.execute()
        
    def tearDown(self):
        shutil.rmtree(self.tmpDir)

    def test_backupOldConfiguration(self):
        backupPath = os.path.join(self.tmpDir, 'etc/kforge.conf.old')
        self.assertTrue(os.path.exists(backupPath))


class UpgradeDbTo0Point10Test(unittest.TestCase):
    """
    For test to work you need to provide a db dump of a 0.9 db and provide link
    to it below and also edit the other values to reflect your setup.
    """
    
    oldSql = os.path.normpath('~/db_dumps/kforge_0.9.sql')
    # edit these values to reflect the state of your original install
    numberOfUsers = 31
    numberOfProjects = 10
    personName = 'rgrp'
    # put a project on which personName is an administrator
    projectName = 'kforge'
    
    def setUp(self):
        upgradeCmd = kforge.utils.upgrade.UpgradeDbTo0Point10()
        upgradeCmd.pgsqlCommand('dropdb')
        upgradeCmd.pgsqlCommand('createdb')
        upgradeCmd.pgsqlCommand('psql', '-q --file %s' % self.oldSql)
        upgradeCmd.execute()
        import kforge.dom
        self.registry = kforge.dom.DomainRegistry()
    
    def _test_basic(self):
        persons = self.registry.persons
        self.failUnless('admin' in persons)
        self.failUnless('visitor' in persons)
        self.failIf('guest' in persons)
        self.failUnless(len(persons) == self.numberOfUsers)
        self.failUnless(self.personName in persons)
        
        projects = self.registry.projects
        self.failUnless('administration' in projects)
        self.failUnless(self.projectName in projects)
        self.failUnless(len(projects) == self.numberOfProjects)
        
        roles = self.registry.roles
        testPerson = persons[self.personName]
        testProject = projects[self.projectName]
        self.failUnless(testPerson in testProject.members)
        self.failUnless(testProject.members[testPerson].role == roles['Administrator'])

    def test_upgrade(self):
        "All in one tests because setup takes so long."
        self._test_basic()


class UpgradeDbTo0Point11Test(UpgradeDbTo0Point10Test):
    
    oldSql = os.path.normpath('~/db_dumps/kforge_0.10.sql')
    numberOfUsers = 36
    numberOfProjects = 16
    
    def setUp(self):
        upgradeCmd = kforge.utils.upgrade.UpgradeDbTo0Point11()
        upgradeCmd.pgsqlCommand('dropdb')
        upgradeCmd.pgsqlCommand('createdb')
        upgradeCmd.pgsqlCommand('psql', '-q --file %s' % self.oldSql)
        upgradeCmd.execute()
        # now we can use stuff that affects the db
        app = kforge.getA()
        self.registry = app.registry
    
    def _test_0point11(self):
        # test purpose has disappeared
        # concerned this tests model rather than db ...
        project = self.registry.projects[self.projectName]
        try:
            pp = project.purpose
        except:
           pass
        else:
           fail('Purpose attribute should not exist')
        # plugins are now dated and stateful
        plugin = self.registry.plugins['accesscontrol']
        self.assertEqual(1, plugin.state.id)
        self.assertTrue(len(str(plugin.dateCreated)) > 0)

    def test_upgrade(self):
        self._test_basic()
        self._test_0point11()
    

def createDevelopmentData():
    "Create the data used for testing in development mode"
    import kforge.command.initialise
    initialiseCmd = kforge.command.initialise.InitialiseDomainModel()
    initialiseCmd.createTestPlugins()
    initialiseCmd.setUpTestFixtures()

if __name__ == '__main__':
    # suite = unittest.makeSuite(UpgradeDbTo0Point10Test)
    suites = [ 
        unittest.makeSuite(UpgradeDataTo0Point11Test),
        unittest.makeSuite(UpgradeDbTo0Point11Test),
        ]
    testRunner = unittest.TextTestRunner()
    testRunner.run(unittest.TestSuite(suites))
    createDevelopmentData()
