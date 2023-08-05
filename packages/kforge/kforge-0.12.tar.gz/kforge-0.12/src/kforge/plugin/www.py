"""
ProjectHome Plugin

This creates a project web directory that is accessible via dav.
"""
import os
import shutil

import kforge.plugin.base
import kforge.url

class Plugin(kforge.plugin.base.SingleServicePlugin):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
    
    def onServiceCreate(self, service):
        """
        For www since a single service plugin only want the plugin directory
        and do not need a service subdirectory
        """
        if service and service.plugin and service.plugin.name == self.domainObject.name:
            self.ensureProjectPluginDirectoryExists(service)
    
    def onServicePurge(self, service):
        if service and service.plugin and service.plugin.name == self.domainObject.name:
            projectPluginPath = self.paths.getProjectPluginPath(service.project, service.plugin)
            if os.path.exists(projectPluginPath):
                shutil.rmtree(projectPluginPath)
    
    def getApacheConfig(self, service):
        """
        Note: allow access to everyone -- even guest
        """
        fsPath = self.paths.getProjectPluginPath(service.project, service.plugin)
        result = 'Alias %(urlPath)s ' + fsPath
        return result

