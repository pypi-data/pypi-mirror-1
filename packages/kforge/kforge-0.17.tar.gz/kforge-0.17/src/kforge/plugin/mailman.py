"""
KForge Mailman plugin.

Installing this plugin allows users to create mailman services to provide
mailing lists associated with their project.

## Installation ##

1. To use this plugin you must have already installed mailman. You should also
have mailman web interface running (see the mailman installation instructions
for how to set this up).

2. KForge config file. Add the following to your KForge configuration file
   setting the variables as needed for your system:

[mailman]
# set this to the fully qualified domain name for your mailing lists
# example: lists.domain.com (NB: no http and no trailing url)
# NB: expect that mailman web interface will have been mounted there
# If this is a problem (e.g. you want to have the email host and web host to be
# different) you will have to make some modifications to the mailman plugin
# code.
mailman_url = lists.somedomain.com

# the base (no arguments) shell command to use when creating a list
newlist = sudo newlist 

# the base (no arguments) shell command to use when deleting a list
rmlist = sudo rmlist

# this is the password that will be used for new mailing lists
list_admin_password = change_this_password_immediately 

3. Install and enable this plugin in the usual way (see the KForge Guide
   for details).
"""
import os
import commands
import shutil
import kforge.plugin.base
import kforge.utils.backup
from kforge.ioc import RequiredFeature
from kforge.dictionarywords import *

class Plugin(kforge.plugin.base.ServicePlugin):
    "Mailman plugin."
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.assertServicesFolder(service)
            listName = self._getFullListName(service)
            adminEmail = self._getAdminEmail(service)
            adminPass = self.dictionary['mailman.list_admin_password']
            self.createMailingList(
                listName=listName,
                adminEmail=adminEmail,
                adminPass=adminPass
            )
            msg = 'MailmanPlugin: Created service list %s.' % listName
            self.log(msg)
    
    def onServicePurge(self, service):
        if self.isOurs(service):
            listName = self._getListName(service)
            adminEmail = self._getAdminEmail(service)
            self.deleteMailingList(
                listName=listName
            )
            msg = 'MailmanPlugin: Deleted service list %s.' % listName
            self.log(msg)

    def _getListName(self, service):
        return service.project.name + '-' + service.name

    def _getFullListName(self, service):
        domain = self.dictionary['mailman.mailman_url']
        short = self._getListName(service)
        return short + '@' + domain

    def _getAdminEmail(self, service):
        adminRole = self.registry.roles['Administrator']
        for member in service.project.members:
            if member.role.name == adminRole.name:
                return member.person.email

    def getApacheConfig(self, service):
        domain = self.dictionary['mailman.mailman_url']
        baseUrl = 'http://%s/mailman/listinfo/' % domain
        listUrl =  baseUrl + self._getListName(service)
        config = ''' 
            Redirect %(urlPath)s ''' + listUrl + '\n'
        return config
    
    def backup(self, service, backupPathBuilder):
        # TODO
        pass

    def createMailingList(self, listName='', adminEmail='', adminPass=''):
        """Create mailing list with newlist command with arguments provided.

        NB: listName can include domain name.
        """
        create_command = self.dictionary['mailman.newlist']
        cmd = create_command + ' ' + listName + ' ' + adminEmail + ' ' + adminPass
        self.runCommand(cmd)

    def deleteMailingList(self, listName=''):
        """Delete mailing list with name listName.
        
        NB: listName *cannot* include domain name.
        """
        delete_command = self.dictionary['mailman.rmlist']
        cmd = delete_command + ' -a ' + listName
        self.runCommand(cmd)

    def runCommand(self, cmd):
        status, output = commands.getstatusoutput(cmd)
        if status:
            msg = "Mailman error: cmd '%s' caused error: %s" % (cmd, output)
            raise Exception(msg)

