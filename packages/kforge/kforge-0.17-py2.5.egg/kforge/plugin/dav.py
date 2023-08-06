"""
KForge dav Plugin.

Enabling this plugin gives dav access to the project directory and all
subdirectories.

## Installation ##

1. Dependencies. To create services using this plugin you must have installed
   the following external applications:

   * Apache dav module (mod_dav). Note that on many systems this will be
     installed by default.

2. KForge config file. You do not need to add anything to the KForge config
   file.
"""
import os
import shutil

import kforge.plugin.base
from dm.strategy import FindProtectionObject

class Plugin(kforge.plugin.base.SingleServicePlugin):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.paths.assertProjectFolder(service.project)

    def getApacheConfig(self, service):
        projectPath = self.paths.getProjectPath(service.project)
        result = 'Alias %(urlPath)s ' + projectPath
        # 'ForceType text/plain' so DAV interprets all file types as text.
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
        # Todo: Pull various bits of access controller setup together under the name 'setupAccessControl'.
        super(Plugin, self).onCreate()
        protectionObject = FindProtectionObject(self.domainObject).find()
        # Don't allow Friends to read the DAV plugin, as it gives access to all project data.
        permission = protectionObject.permissions[self.registry.actions['Read']]
        friend = self.registry.roles['Friend']
        if permission in friend.grants:
            grant = friend.grants[permission]
            grant.delete()
        # Don't allow Developers to write to the DAV plugin, as it gives access to all project data.
        permission = protectionObject.permissions[self.registry.actions['Update']]
        friend = self.registry.roles['Developer']
        if permission in friend.grants:
            grant = friend.grants[permission]
            grant.delete()

