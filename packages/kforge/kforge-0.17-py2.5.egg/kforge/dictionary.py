"""
Dictionary of system attributes.

"""

import os
import sys
import dm.dictionary
import kforge
import kforge.dictionarywords
from kforge.dictionarywords import *

class SystemDictionary(dm.dictionary.SystemDictionary):

    words = kforge.dictionarywords

    def getSystemName(self):
        return 'kforge'

    def getSystemServiceName(self):
        return 'KForge'

    def getSystemVersion(self):
        return kforge.__version__
 
    def setDefaultWords(self):
        super(SystemDictionary, self).setDefaultWords()
        self[MEMBER_ROLE_NAME] = 'Friend'
        self[PLUGIN_PACKAGE_NAME] = 'kforge.plugin'
        self[SVN_ADMIN_SCRIPT] = 'svnadmin'
        self[TRAC_ADMIN_SCRIPT] = 'trac-admin'
        self[TRAC_TEMPLATES_PATH] = ''
        self[TRAC_HTDOCS_PATH] = ''
        self[PROJECTS_PATH] = ''
        self[MERCURIAL_ADMIN_SCRIPT] = 'hg'
        self[GIT_ADMIN_SCRIPT] = 'git'
        self[DAV_LOCK_PATH] = ''
        self[FEED_LENGTH] = '100'
        self[FEED_SUMMARY_LENGTH] = '25'
