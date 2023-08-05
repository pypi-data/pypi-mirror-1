"""
KForge AccessControl plugin.

"""

import kforge.plugin.base
import os

class Plugin(kforge.plugin.base.NonServicePlugin):
    "AccessControl plugin."
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        name = 'accesscontrol'

    def getProtectionClass(self):
        return self.registry.getDomainClass('ProtectionObject')

    def makeProtectedName(self, protectedObject):
        protectionClass = self.getProtectionClass()
        return protectionClass.makeProtectedName(protectedObject)

    def createProtectionObject(self, protectedObject):
        protectedName = self.makeProtectedName(protectedObject)
        return self.registry.protectionObjects.create(protectedName)
        
    def findProtectionObject(self, protectedObject):
        protectedName = self.makeProtectedName(protectedObject)
        return self.registry.protectionObjects.get(protectedName, None)
        
    def onPersonCreate(self, person):
        protectionObject = self.findProtectionObject(person)
        if not protectionObject: 
            protectionObject = self.createProtectionObject(person)
        for permission in protectionObject.permissions:
            if not permission in person.grants:
                person.grants.create(permission)
    
    def onPersonPurge(self, person):
        protectionObject = self.findProtectionObject(person)
        if protectionObject:
            protectionObject.delete()

