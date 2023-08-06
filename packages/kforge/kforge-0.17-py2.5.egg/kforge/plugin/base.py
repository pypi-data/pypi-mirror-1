import dm.plugin.base
import os
from dm.strategy import FindProtectionObject
from dm.strategy import CreateProtectionObject
from dm.dictionarywords import APACHE_RELOAD_CMD
import dm.times

class AbstractServicePlugin(dm.plugin.base.PluginBase):
    """
    Service plugins deploy adapted software applications as project services.
    """ 

    def checkDependencies(self):
        errors = []
        return errors

    def showDepends(self):
        return [
        ]
    showDepends = classmethod(showDepends)

    def getMaxServicesPerProject(self):
        raise Exception("Abstract method not implemented.")

    def isOurs(self, service):
        "Checks whether a service belongs to this plugin."
        return service and service.plugin and \
            service.plugin.name == self.domainObject.name
    
    def ensureProjectPluginDirectoryExists(self, service):
        self.assertServicesFolder(service)

    def assertServicesFolder(self, service):
        path = self.paths.getProjectPluginPath(service.project, service.plugin)
        self.paths.assertFolder(path, 'project %s services' % service.plugin.name)
    
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

    def getUserHelp(self, service, serviceLocation):
        """Provide a service user help message.
        """
        return ''

    def getStatusMessage(self, service):
        """Provide a service status message.
        """
        # Todo: Check at least whether HEAD gets a 404?
        if not self.dictionary[APACHE_RELOAD_CMD]:
            msg = "Configuration created."
            if dm.times.getUniversalNow() - service.dateCreated < 86400:
                msg += " You may need to wait for the server to restart."
        elif service.isSystemUpSinceModified():
            msg = "Running."
        else:
            msg = "Waiting for new configuration to load."
        return msg

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

    def onServicePurge(self, service):
        if self.isOurs(service):
            self.trashServiceFolder(service)

    def trashServiceFolder(self, service):
        servicePath = self.paths.getServicePath(service)
        msg = "%sPlugin: Trashing service folder: %s" % (self.domainObject.name.capitalize(), servicePath)
        self.logger.info(msg)
        if not os.path.exists(servicePath):
            return
        self.paths.assertTrashFolder()
        trashPath = self.paths.getTrashPath()
        trashBase = os.path.join(trashPath, str(service.id))
        trashNew = trashBase
        trashIndex = 0
        while os.path.exists(trashNew):
            trashNew = "%s.%s" % (trashBase, trashIndex)
            trashIndex += 1
        try:
            import shutil
            shutil.move(servicePath, trashNew)
        except Exception, inst:
            msg = "Couldn't move service files into trash: tried moving %s to %s: %s" % (
                servicePath, trashNew
            )


class ServicePlugin(AbstractServicePlugin):
    
    def getMaxServicesPerProject(self):
        return None

        
class SingleServicePlugin(AbstractServicePlugin):

    def getMaxServicesPerProject(self):
        return 1


class NonServicePlugin(AbstractServicePlugin):

    def getMaxServicesPerProject(self):
        return 0

