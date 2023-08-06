import os

import kforge.plugin.base
import kforge.apache.apacheconfig
import kforge.utils

class Plugin(kforge.plugin.base.NonServicePlugin):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.configBuilder = kforge.apache.apacheconfig.ApacheConfigBuilder()
    
    def rebuildAndReload(self):
        self.configBuilder.buildConfig()
        self.configBuilder.reloadConfig()
        
    def onServiceCreate(self, service):
        self.rebuildAndReload()
    
    def onServiceUpdate(self, service):
        self.rebuildAndReload()
    
    def onServiceDelete(self, service):
        self.rebuildAndReload()
    
