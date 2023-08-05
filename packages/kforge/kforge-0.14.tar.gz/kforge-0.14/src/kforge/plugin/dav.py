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
        findObject = FindProtectionObject(self.domainObject)
        protectionObject = findObject.find()
        read = protectionObject.permissions[self.registry.actions['Read']]
        friend = self.registry.roles['Friend']
        if read in friend.grants:
            grant = friend.grants[read]
            grant.delete()

