import dm.cli.admin
import dm.environment
import os
import sys

class AdministrationUtility(dm.cli.admin.AdministrationUtility):

    def buildApplication(self):
        import kforge.soleInstance
 
    def do_updatefeed(self, line=None):
        args = self.convertLineToArgs(line)
        if len(args) != 0:
            print 'Error: Unexpected arguments\n'
            self.help_updatefeed(line)
            return 1
        self.updateFeedEntries()

    def updateFeedEntries(self):
        # Loop over Trac projects.
        from kforge.soleInstance import application
        from kforge.ioc import RequiredFeature
        accessController = RequiredFeature('AccessController')
        if 'trac' in application.registry.plugins:
            tracPlugin = application.registry.plugins['trac']
        else:
            print "Warning: The 'trac' plugin is not enabled."
            return 1
        from kforge.url import UrlScheme
        urls = UrlScheme()
        sourceUrls = []
        tracServices = tracPlugin.services
        print "Aggregating from the following locations (set 'domain_name' if necessary):"
        for service in tracServices:
            if accessController.isAuthorised(None, 'Read', service.plugin, service.project):
                sourceUrl = urls.getServiceUrl(service) + '/timeline?ticket=on&changeset=on&milestone=on&wiki=on&max=50&daysback=90&format=rss'
                sourceUrls.append(sourceUrl)
                print sourceUrl
        application.registry.feedentries.readSources(sourceUrls)
        application.registry.feedentries.truncate()
        print "Feed summary now:"
        for e in application.registry.feedentries.listSummary():
            print e.updated, e.source, e.title

    def help_updatefeed(self, line=None):
        usage = \
'''updatefeed

Update feeds from site services.'''
        print usage

    def do_fs(self, line=None):
        args = self.convertLineToArgs(line)
        if len(args) == 0:
            print 'Error: Insufficient arguments\n'
            self.help_fs(line)
            return 1
        elif args[0] == 'create':
            try:
                self.createFilesystem()
                return 0
            except Exception, inst:
                print "Error: Couldn't create filesystem: %s" % str(inst)
        else:
            self.help_fs()
            return 1

    def createFilesystem(self):
        import kforge.cli.data
        installer = kforge.cli.data.InstallData()
        installer.execute()

    def help_fs(self, line=None):
        usage = \
'''fs create 

Install template and media files to filesystem paths set in your
KForge configuration file (see 'templates_dir' and 'media_dir').
'''
        print usage

    def do_data(self, line=None):
        return self.do_fs(line)

    def help_data(self, line=None):
        return self.help_fs(line)

    def do_plugin(self, line=None):
        args = self.convertLineToArgs(line)

        if len(args) == 0:
            print 'Error: Insufficient arguments\n'
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

        hiddenServiceNames = ['example', 'example_non_service', 'example_single_service', 'testingexample', 'apacheconfig', 'accesscontrol']
        if actionName == 'choices':
            pluginNames = [e.name for e in plugin_points]
            pluginNames.sort()
            for name in pluginNames:
                if name not in hiddenServiceNames:
                    print name
            return 0
        if actionName == 'list':
            for plugin in registry.plugins:
                if plugin.name not in hiddenServiceNames:
                    print plugin.name
            return 0
        if not pluginName:
            print 'Error: Plugin name required. See command help for details.'
            return 1
        if actionName == 'enable':
            if pluginName not in registry.plugins:
                try:
                    plugin = registry.plugins.create(pluginName)
                    if not plugin.getSystem():
                        raise Exception("No plugin named '%s'." % pluginName)
                    dependencyErrors = plugin.getSystem().checkDependencies()
                    if dependencyErrors:
                        print "Error: The plugin's dependencies didn't check out:"
                        for e in dependencyErrors:
                            print e
                        plugin.delete()
                        plugin.purge()
                        print
                        print "Please refer to 'doc %s' for more information." % pluginName
                        return 1
                    else:
                        msg = '''The '%s' plugin is now enabled (see 'doc' and 'show').''' % (pluginName)
                        print msg
                        return 0
                except Exception, inst:
                    if pluginName in registry.plugins:
                        del(registry.plugins[pluginName])
                    msg = "Error: Couldn't create '%s' plugin: %s" % (pluginName, str(inst))
                    print msg
                    return 1
            else:
                msg = '''The '%s' plugin is already enabled.''' % (pluginName)
                print msg
                return 0
        elif actionName == 'show' or actionName == 'status':
            try:
                pluginClass = pluginFactory.getPluginClass(pluginName)
                if not pluginClass:
                    raise Exception("No plugin named '%s'." % pluginName)
            except Exception, inst:
                print "Error: %s" % str(inst)
                return 1
            print "Package: %s" % pluginClass.__module__
            try:
                pluginObject = registry.plugins.getAll()[pluginName]
            except:
                pluginObject = None
            if pluginObject:
                if pluginObject.isActive():
                    pluginState = 'enabled'
                else:
                    pluginState = 'disabled'
            else:
                pluginState = 'not enabled'
            print "State: %s" % pluginState
            print "Depends:"
            for line in pluginClass.showDepends():
                print " %s" % line
            pluginServices = pluginObject and pluginObject.services or []
            print "Services:"
            paths = RequiredFeature('FileSystem')
            for service in pluginServices:
                print " %s %s %s" % (service.project.name, service.name, str(paths.getServicePath(service)))
           
        elif actionName == 'disable':
            if pluginName in registry.plugins:
                del(registry.plugins[pluginName])
                print "Plugin '%s' has been disabled. Existing '%s' services" % (pluginName, pluginName)
                print "remain unaffected. Users will not be able to create"
                print "new services until the plugin has been enabled again."
                return 0
            else:
                msg = "The '%s' plugin is already disabled." % (pluginName)
                print msg
                return 0
        elif actionName == 'doc':
            # bit of a hack until we move docstring into plugin class from
            # module
            try:
                plugin_system = pluginFactory.getPluginClass(pluginName)
                pluginPackage = __import__(plugin_system.__module__, '', '', '*')
                print pluginPackage.__doc__
                return 0
            except Exception, inst:
                msg = "Couldn't get doc for '%s' plugin: %s" % (
                    pluginName, str(inst)
                )
                print msg
                return 1
        else:
            self.help_plugin()
            return 1

    def help_plugin(self, line=None):
        usage = \
'''plugin {action} [plugin-name]

{action} is one of: choices | list | doc | show | enable | disable

  * choices: list the available plugins installed on the system.
  * list: list the enabled plugins available for use by project.
  * doc: documentation on the specified plugin including details of any
    additional software that needs to be installed to use the plugin's
    functionality.
  * show: status of the plugin, indicates status of dependencies, and
    lists all project services that have been created with this plugin.
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
        return '%s %s' % (systemName, systemVersion)


class UtilityRunner(dm.cli.admin.UtilityRunner):

    systemName = 'kforge'
    utilityClass = AdministrationUtility
    usage  = """Usage: %prog [options] [command]

Administer a KForge service, including its domain objects. 

To obtain information about the commands available run the "help" command.

    $ kforge-admin help

Domain objects (e.g. persons, projects, etc) can be administered by starting
a python shell from within interactive mode. Run "help shell" for more details.

Report bugs to <bugs@appropriatesoftware.net>."""

