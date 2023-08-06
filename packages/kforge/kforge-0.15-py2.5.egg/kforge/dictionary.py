"""
Dictionary of system attributes.

"""

import os
import sys
import dm.dictionary
import kforge
from kforge.dictionarywords import *

class SystemDictionary(dm.dictionary.SystemDictionary):

    def getSystemName(self):
        return 'kforge'

    def getSystemVersion(self):
        return kforge.__version__
 
    def setDefaultWords(self):
        super(SystemDictionary, self).setDefaultWords()
        self[MEMBER_ROLE_NAME] = 'Friend'
        self[PLUGIN_PACKAGE_NAME] = 'kforge.plugin'
        self[TRAC_ADMIN_SCRIPT] = 'trac-admin'

