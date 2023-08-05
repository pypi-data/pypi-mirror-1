import unittest
import kforge.testunit

def suite():
    suites = [
        unittest.makeSuite(PluginTest),
        ]
    return unittest.TestSuite(suites)

class PluginTest(kforge.testunit.TestCase):

    def setUp(self):
        super(PluginTest, self).setUp()
        self.msgStack = []
        self.pluginName = 'notify'
        if not self.registry.plugins.has_key(self.pluginName):
            self.registry.plugins.create(self.pluginName)
        self.plugin = self.registry.plugins[self.pluginName]
        self.pluginSystem = self.plugin.getSystem()
        # bit of a hack to disable the email listener
        self.pluginSystem.listeners.pop(0)
        self.pluginSystem.registerListener(self.listen)
        self.project = self.registry.projects['annakarenina']
        self.person = self.registry.persons['levin']
        self.projectAdmins = self.pluginSystem._getProjectAdmins(self.project)
    
    def listen(self, msg, users):
       self.msgStack.append(msg)

    def test__getProjectAdmins(self):
        self.failUnless('levin' in self.projectAdmins)

    def test_notifyListeners(self):
        msg = 'Test message'
        self.pluginSystem.notifyListeners(msg)
        self.pluginSystem.notifyListeners(msg, self.projectAdmins)

    def test_onProjectCreate(self):
        # fake the creation of a project
        self.plugin.getSystem().onProjectCreate(self.project)
        exp_msg = 'Project created: %s' % self.project.name
        self.failUnless(exp_msg in self.msgStack[-1])

    def test_onProjectDelete(self):
        # fake the creation of a project
        self.plugin.getSystem().onProjectDelete(self.project)
        exp_msg = 'Project deleted: %s' % self.project.name
        self.failUnless(exp_msg in self.msgStack[-1])

    def test_onPersonCreate(self):
        # fake the creation of a project
        self.plugin.getSystem().onPersonCreate(self.person)
        exp_msg = 'Person created: %s' % self.person.name
        self.failUnless(exp_msg in self.msgStack[-1])

    def test_emailNotify(self):
        # not a proper unit test because we cannot verify email is sent
        msg = 'It is a truth universally acknowledged'
        users = ['admin']
        self.pluginSystem.emailNotify(msg, users)

