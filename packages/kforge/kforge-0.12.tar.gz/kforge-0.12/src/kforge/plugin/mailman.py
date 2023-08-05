"""
KForge Mailman plugin. Enabling this plugin allows users to create mailman
services to provide mailing lists associated with their project.

## Installation ##

1. To use this plugin you must have already installed mailman. You should also
have mailman web interface running (see the mailman installation instructions
for how to set this up).

2. Add the following configuration to your kforge configuration file

[mailman]
# set this to the fully qualified domain name for your mailing lists
# example: lists.domain.com (NB: no http and no trailing url)
# NB: expect that mailman web interface will have been mounted there
mailman_url = http://somedomain.com/mailman/listinfo

# the base (no arguments) shell command to use when creating a list
newlist = sudo newlist 

# the base (no arguments) shell command to use when deleting a list
rmlist = sudo rmlist

# this is the password that will be used for new mailing lists
list_admin_password = change_this_password_immediately 

3. Install and enable this plugin in the usual way (see the KForge
Documentation for details)
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
        if service and service.plugin and service.plugin.name == 'mailman':
            listName = self.getListName(service)
            adminEmail = self.getAdminEmail(service)
            adminPass = self.dictionary['mailman.list_admin_password']
            self.createMailingList(
                listName=listName,
                adminEmail=adminEmail,
                adminPass=adminPass
            )
            msg = 'MailmanPlugin: Created service list %s.' % listName
            self.log(msg)
    
    def onServicePurge(self, service):
        if service and service.plugin and service.plugin.name == 'mailman':
            listName = self.getListName(service)
            adminEmail = self.getAdminEmail(service)
            self.deleteMailingList(
                listName=listName
            )
            msg = 'MailmanPlugin: Deleted service list %s.' % listName
            self.log(msg)

    def getListName(self, service):
        domain = self.dictionary['mailman.mailman_url']
        return service.project.name + '-' + service.name + '@' + domain

    def getAdminEmail(self, service):
        adminRole = self.registry.roles['Administrator']
        for member in service.project.members:
            if member.role.name == adminRole.name:
                return member.person.email

    def getApacheConfig(self, service):
        domain = self.dictionary['mailman.mailman_url']
        baseUrl = 'http://%s/mailman/listinfo/' % domain
        listUrl =  baseUrl + self.getListName(service)
        config = ''' 
            Redirect %(urlPath)s ''' + listUrl + '\n'
        return config
    
    def backup(self, service, backupPathBuilder):
        # TODO
        pass

    def createMailingList(self, listName='', adminEmail='', adminPass=''):
        create_command = self.dictionary['mailman.newlist']
        cmd = create_command + ' ' + listName + ' ' + 'adminEmail' + ' ' + adminPass
        self.runCommand(cmd)

    def deleteMailingList(self, listName=''):
        delete_command = self.dictionary['mailman.rmlist']
        cmd = delete_command + ' -a ' + listName
        self.runCommand(cmd)

    def runCommand(self, cmd):
        status, output = commands.getstatusoutput(cmd)
        if status:
            msg = "Mailman error: cmd '%s' caused error: %s" % (cmd, output)
            raise Exception(msg)

