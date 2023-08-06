import os
import sys

import dm.environment
import dm.cli.admin

class AdministrationUtility(dm.cli.admin.AdministrationUtility):

    def buildApplication(self):
        import kforge.soleInstance

    def initialiseSystemServiceFilesystem(self):
        import kforge.cli.data
        installer = kforge.cli.data.InstallData()
        installer.execute()

    def do_data(self, line=None):
        args = self.convertLineToArgs(line)
        if len(args) == 0:
            print 'ERROR: Insufficient arguments\n'
            self.help_data(line)
            return 1
        elif args[0] == 'create':
            self.initialiseSystemServiceFilesystem()
            return 0
        else:
            self.help_data()
            return 1

    def help_data(self, line=None):
        usage = \
'''data create 

Install environment data including templates, htdocs, media. The values
in your configuration will be used to create filesystem files.
'''
        print usage

    def do_plugin(self, line=None):
        args = self.convertLineToArgs(line)

        if len(args) == 0:
            print 'ERROR: Insufficient arguments\n'
            self.help_plugin(line)
            return 1
        actionName = args[0]
        if len(args) > 1:
            pluginName = args[1]
        else:
            pluginName = ''

        import kforge.soleInstance
        registry = kforge.soleInstance.application.registry
        from dm.ioc import RequiredFeature
        pluginFactory = RequiredFeature('PluginFactory')
        plugin_points = pluginFactory.getEntryPoints()

        # TODO: could list which plugins are already installed using register
        if actionName == 'list':
            for en in plugin_points:
                print en.name
            return 0

        if not pluginName:
            print 'ERROR: Plugin name required. See command help for details.'
            return 1
        if actionName == 'enable':
            registry.plugins.create(pluginName)
            msg = \
'''SUCCESS.

Please note that for this plugin to be fully operational you may need to
install some additional software. For more information please see the plugin's
documentation:

    kforge-admin plugin doc %s
''' % pluginName
            print msg
            return 0
        elif actionName == 'disable':
            del(registry.plugins[pluginName])
            return 0
        elif actionName == 'doc':
            # bit of a hack until we move docstring into plugin class from
            # module
            plugin_system = pluginFactory.getPluginClass(pluginName)
            pluginPackage = __import__(plugin_system.__module__, '', '', '*')
            print pluginPackage.__doc__
            return 0
        else:
            self.help_plugin()
            return 1

    def help_plugin(self, line=None):
        usage = \
'''plugin {action} [plugin-name]

{action} is one of: list | doc | enable | disable

  * list: list the plugins installed on the system and thus available for use
    with this service (so all plugins available whether enabled or disabled).
  * doc: documentation on the specified plugin including details of any
    additional software that needs to be installed to use the plugin's
    functionality.
  * enable: enable the specified plugin on this KForge service.
  * disable: disable the specified plugin on this KForge service. Warning: you
    will not be able to delete a plugin if it has any associated services.
'''
        print usage

    def backupSystemService(self):
        import kforge.soleInstance
        commandSet = kforge.soleInstance.application.commands
        backupCommandName = 'Backup'
        backupCommand = commandSet[backupCommandName](self.args[0])
        backupCommand.execute()

    def createFilesDumper(self):
        from kforge.migrate import FilesDumper
        return FilesDumper()

    def takeDatabaseAction(self, actionName):
        from kforge.utils.db import Database
        db = Database()
        actionMethod = getattr(db, actionName)
        actionMethod()

    def upgradeSystemServiceDatabase(self):
        # TODO fix this to be generic
        import kforge.utils.upgrade
        dbCommand = kforge.utils.upgrade.UpgradeDbTo0Point14()
        dbCommand.execute()
        # print 'No changes required.'

    def upgradeSystemServiceFilesystem(self):
        # ditto here with filesystem
        # should make this generic 
        # import kforge.utils.upgrade
        # filesystemCommand = kforge.utils.upgrade.UpgradeDataTo0Point11(
        #     self.servicePath, self.systemPath
        # )
        # filesystemCommand.execute()
        # nothing in fact to do
        print 'No changes required.'

    def getApacheConfigBuilderClass(self):
        from kforge.apache.apacheconfig import ApacheConfigBuilder
        return ApacheConfigBuilder

    def getSystemName(self):
        return "KForge"
        
    def getSystemVersion(self):
        import kforge
        return kforge.__version__
        
    def createAboutMessage(self):
        systemName = self.getSystemName()
        systemVersion = self.getSystemVersion()
        aboutMessage = \
'''This is %s version %s.

Copyright the Open Knowledge Foundation. KForge is open-source 
software licensed under the GPL v2.0. See COPYING for details.
''' % (systemName, systemVersion)
        return aboutMessage

class UtilityRunner(dm.cli.admin.UtilityRunner):

    systemName = 'kforge'
    utilityClass = AdministrationUtility
    usage  = """Usage: %prog [options] [command]

Administer a KForge service, including its domain objects. 

Can be run in two modes:
   1. single command: run the command provided and exit (Default)
   2. interactive (use the "--interactive" option)

To obtain information about the commands available run the "help" command.

Domain objects (e.g. persons, projects, etc) are administered by starting
a python shell from within interactive mode. Run "help shell" for more details.

"""

