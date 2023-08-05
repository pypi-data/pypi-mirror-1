import dm.environment
import dm.cli.admin

class AdministrationUtility(dm.cli.admin.AdministrationUtility):

    def buildApplication(self):
        import kforge.soleInstance

    def initialiseSystemServiceFilesystem(self):
        print 'WARNING: This command is not implemented.'
        return 0

    def backupSystemService(self):
        import kforge.soleInstance
        commandSet = kforge.soleInstance.application.commands
        backupCommandName = 'Backup'
        backupCommand = commandSet[backupCommandName](self.args[0])
        backupCommand.execute()

    def takeDatabaseAction(self, actionName):
        from kforge.utils.db import Database
        db = Database()
        actionMethod = getattr(db, actionName)
        actionMethod()

    def upgradeSystemServiceDatabase(self):
        # TODO this is for 0.11 need to fix this to be generic
        # import kforge.utils.upgrade
        # dbCommand = kforge.utils.upgrade.UpgradeDbTo0Point11()
        # dbCommand.execute()
        pass

    def upgradeSystemServiceFilesystem(self):
        # ditto here with filesystem
        # should make this generic 
        # import kforge.utils.upgrade
        # filesystemCommand = kforge.utils.upgrade.UpgradeDataTo0Point11(
        #     self.servicePath, self.systemPath
        # )
        # filesystemCommand.execute()
        # nothing in fact to do for 0.12
        pass

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

    system_name = 'kforge'
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

