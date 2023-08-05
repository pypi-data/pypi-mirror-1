"""
Dav Plugin

This gives dav access to the project directory and all subdirectories.
As such does not create its own plugin directory
"""
import os
import shutil

import kforge.plugin.base

class Plugin(kforge.plugin.base.SingleServicePlugin):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
    
    def getApacheConfig(self, service):
        projectDirPath = self.paths.getProjectPath(service.project)
        result = 'Alias %(urlPath)s ' + projectDirPath
        # ForceType text/plain so that dav interprets all file types as text
        result += """
            <Location %(urlPath)s>
                DAV On
                Options +Indexes
                # Remove use DirectoryIndex
                DirectoryIndex none.none.none
                ForceType text/plain
                
                %(accessControl)s
            </Location>"""
        return result
    
    def onCreate(self):
        """
        Only allow members to read: dav plugin gives access to all project data.
        """
        super(Plugin, self).onCreate()
        protectionClass = self.registry.getDomainClass('ProtectionObject')
        protectedName = protectionClass.makeProtectedName(self.domainObject)
        protectionObjects = self.registry.protectionObjects
        protectionObject = protectionObjects[protectedName]
        read = protectionObject.permissions[self.registry.actions['Read']]
        friend = self.registry.roles['Friend']
        if read in friend.grants:
            grant = friend.grants[read]
            grant.delete()

