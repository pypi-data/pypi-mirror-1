import dm.plugin.base
import os
from dm.strategy import FindProtectionObject
from dm.strategy import CreateProtectionObject

class AbstractServicePlugin(dm.plugin.base.PluginBase):

    def getMaxServicesPerProject(self):
        raise "Abstract method not implemented."
    
    def ensureProjectPluginDirectoryExists(self, service):
        """
        Check project plugin directory exists and, if it does not, create it
        """
        projectPluginPath = self.paths.getProjectPluginPath(
            service.project, service.plugin
        )
        if not os.path.exists(projectPluginPath):
            os.makedirs(projectPluginPath)
    
    def backup(self, service, backupPathBuilder):
        """Backup the plugged-in application service.

        @backupPathBuilder: any object supporting a function getServicePath.
        """
        pass
    
    def onCreate(self):
        createObject = CreateProtectionObject(self.domainObject)
        protectionObject = createObject.create()
        import kforge.command
        cmd = kforge.command.GrantStandardProjectAccess(protectionObject)
        cmd.execute()
    
    def onDelete(self):
        findObject = FindProtectionObject(self.domainObject)
        protectionObject = findObject.find()
        if protectionObject:
            protectionObject.delete()

    def getUserHelp(self, service):
        """Provide a service-related help message for use by the web user
        interface.
        """
        return ''

    def getApacheConfigCommon(self):
        """
        Return a fragment of Apache config that is only needed once per plugin
        per virtual host (so common across all instances
        """
        return ''

    def getApacheConfig(self, service):
        """
        Returns a fragment of apache config appropriate for the plugin instance
        The fragment can use the variables defined in the dictionary in
            ApacheConfigBuilder.getServiceSection
        by inserting them as %(var_name)s
        Alternatively it can build the config itself
        """
        return ''


class ServicePlugin(AbstractServicePlugin):
    
    def getMaxServicesPerProject(self):
        return None

        
class SingleServicePlugin(AbstractServicePlugin):

    def getMaxServicesPerProject(self):
        return 1


class NonServicePlugin(AbstractServicePlugin):

    def getMaxServicesPerProject(self):
        return 0

