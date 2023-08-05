import os
import sys

import dm.environment
import dm.cli.admin

class AdministrationUtility(dm.cli.admin.AdministrationUtility):

    def buildApplication(self):
        import kforge.soleInstance

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

    def initialiseSystemServiceFilesystem(self):
        import kforge.cli.data
        installer = kforge.cli.data.InstallData()
        installer.execute()

    def help_data(self, line=None):
        usage = \
'''data create 

Install environment data including templates, htdocs, media. The values
in your configuration will be used to create filesystem files.
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
        dbCommand = kforge.utils.upgrade.UpgradeDbTo0Point13()
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

    def buildApacheConfig(self):
        from kforge.apache.apacheconfig import ApacheConfigBuilder
        configBuilder = ApacheConfigBuilder()
        configBuilder.buildConfig()

    def reloadApacheConfig(self):
        from kforge.apache.apacheconfig import ApacheConfigBuilder
        configBuilder = ApacheConfigBuilder()
        configBuilder.reloadConfig()

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

