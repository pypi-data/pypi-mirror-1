import os
import commands
import re

import trac

import kforge.command
import kforge.plugin.trac.dom
from kforge.ioc import *
import kforge.exceptions

class TracCommand(kforge.command.Command):
    
    def __init__(self, tracProject):
        super(TracCommand, self).__init__()
        self.tracProject = tracProject
        self.envname = self.tracProject.service.getDirPath()
        self.tracadminBase = 'trac-admin %s ' % self.envname

class AdminUserBaseCommand(TracCommand):
    """
    Notes: must define self.shellCmd in inheriting classes.
    """

    def __init__(self, tracProject, username):
        super(AdminUserBaseCommand, self).__init__(tracProject)
        self.username = username
    
    def execute(self):
        self.status, self.output = commands.getstatusoutput(self.shellCmd)
        if self.status:
            msg = \
'''Error on attempt to execute admin user command on trac environment
associated with service %s.

Shell command was: %s

Output was %s''' % (self.tracProject.service, self.shellCmd, self.output)
            self.logger.warn(msg)

class AddAdminUserCommand(AdminUserBaseCommand):

    def __init__(self, tracProject, username):
        super(AddAdminUserCommand, self).__init__(tracProject, username)
        tracAction = ' permission add %s TRAC_ADMIN '  % self.username
        self.shellCmd = self.tracadminBase + tracAction

class RemoveAdminUserCommand(AdminUserBaseCommand):

    def __init__(self, tracProject, username):
        super(RemoveAdminUserCommand, self).__init__(tracProject, username)
        tracAction = ' permission remove %s TRAC_ADMIN '  % self.username
        self.shellCmd = self.tracadminBase + tracAction

class IsAdminUserCommand(AdminUserBaseCommand):
    """Tests whether the user is a TRAC_ADMIN.
    @rtype: bool
    @return: in result attribute
    """

    def __init__(self, tracProject, username):
        super(IsAdminUserCommand, self).__init__(tracProject, username)
        # user argument only added in trac 0.9
        # tracAction = ' permission list %s'  % self.username
        tracAction = ' permission list'
        self.shellCmd = self.tracadminBase + tracAction
        self.result = None

    def execute(self):
        super(IsAdminUserCommand, self).execute()
        regex = '%s\s* TRAC_ADMIN' % self.username
        searchResult = re.search(regex, self.output)
        if searchResult is not None:
            self.result = True
        else:
            self.result = False

class TracProjectEnvironmentCreate(TracCommand):
    "Command to create a new Trac instance."

    def __init__(self, tracProject):
        super(TracProjectEnvironmentCreate, self).__init__(tracProject)
        self.svnService = self.tracProject.svn

    def execute(self):
        super(TracProjectEnvironmentCreate, self).execute()
        self.assertSvnService()
        self.checkProjectPluginDir()
        self.assertNotTracProjectEnvironmentCreated()
        self.createTracProjectEnvironment()
        self.assertTracProjectEnvironmentCreated()
        self.tracProject.isEnvironmentInitialised = True
        self.tracProject.save()
        self.logger.debug("New Trac environment created: %s" % self.envname)

    def assertSvnService(self):
        if not self.svnService:
            error = "No svn service for trac project %s." % self.tracProject
            self.raiseError(error)

    def checkProjectPluginDir(self):
        self.tracProject.service.checkProjectPluginDir()

    def isTracProjectEnvironmentCreated(self):
        return self.tracProject.service.hasDir() 

    def assertNotTracProjectEnvironmentCreated(self):
        if self.isTracProjectEnvironmentCreated():
            error = "A Trac project environment already exists for trac service %s: %s" % (self.tracProject.service, self.envname)
            self.raiseError(error)

    def assertTracProjectEnvironmentCreated(self):
        if not self.isTracProjectEnvironmentCreated():
            error = "A Trac project environment couldn't be created for service %s." % self.tracProject
            self.raiseError(error)

    def createTracProjectEnvironment(self):
        versionParts = trac.__version__.split('.')
        tracVersion = float(versionParts[0] + '.' + versionParts[1])
        project_name = self.tracProject.service.id
        db_str = 'sqlite:db/trac.db'
        if tracVersion <= 0.8:
            db_str = '' # no db_str stuff in trac <= 0.8
        repository_dir = self.svnService.getDirPath()
        templates_dir = self.dictionary['trac.templates_path']
        cmd = 'trac-admin %s initenv %s %s %s %s' % (self.envname, project_name, db_str, repository_dir, templates_dir)
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.raiseError('Creation of trac project environment failed (cmd was: %s) (output was: %s)' % (cmd, output))

