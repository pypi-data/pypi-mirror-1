"""
KForge AccessControl plugin.

"""

import kforge.plugin.base
import os
from dm.strategy import FindProtectionObject
from dm.strategy import CreateProtectionObject
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS

class Plugin(kforge.plugin.base.NonServicePlugin):
    "AccessControl plugin."
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        name = 'accesscontrol'

    def onPersonCreate(self, person):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        createObject = CreateProtectionObject(person)
        protectionObject = createObject.create()
        for permission in protectionObject.permissions:
            if not permission in person.grants:
                person.grants.create(permission)
    
    def onPersonPurge(self, person):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        findObject = FindProtectionObject(person)
        protectionObject = findObject.find()
        if protectionObject:
            protectionObject.delete()
            
