import dm.plugin.base
import os

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
        pass
    
    def onCreate(self):
        protectionClass = self.registry.getDomainClass('ProtectionObject')
        protectedName = protectionClass.makeProtectedName(self.domainObject)
        protectionObjects = self.registry.protectionObjects
        protectionObject = protectionObjects.create(protectedName)
        import kforge.command
        cmd = kforge.command.GrantStandardProjectAccess(protectionObject)
        cmd.execute()
    
    def onDelete(self):
        protectionClass = self.registry.getDomainClass('ProtectionObject')
        protectedName = protectionClass.makeProtectedName(self.domainObject)
        protectionObjects = self.registry.protectionObjects
        if protectedName in protectionObjects:
            protectionObject = protectionObjects[protectedName]
            protectionObject.delete()

    def getUserHelp(self, service):
        """Provide a service-related help message for use by the web user
        interface.
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

