import os
import commands
import re
import distutils.version
# import inline so that access to docstring works even when trac not installed
# import trac

import kforge.command
import kforge.plugin.trac.dom
from kforge.ioc import *
import kforge.exceptions
from kforge.dictionarywords import TRAC_ADMIN_SCRIPT

class TracCommand(kforge.command.Command):
    
    def __init__(self, tracProject):
        super(TracCommand, self).__init__()
        self.tracProject = tracProject
        self.envname = self.tracProject.service.getDirPath()
        scriptPath = self.dictionary[TRAC_ADMIN_SCRIPT]
        self.tracadminBase = '%s %s ' % (scriptPath, self.envname)


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
            self.logger.error(msg)


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
            error = "A Trac project environment already"
            error += " exists for trac service %s: %s" % (
                self.tracProject.service, self.envname
            )
            self.raiseError(error)

    def assertTracProjectEnvironmentCreated(self):
        if not self.isTracProjectEnvironmentCreated():
            error = "A Trac project environment couldn't be"
            error += " created for service %s." % self.tracProject
            self.raiseError(error)

    def createTracProjectEnvironment(self):
        import trac
        trac_version = distutils.version.LooseVersion(trac.__version__)
        v0_9 = distutils.version.LooseVersion('0.9')
        v0_10 = distutils.version.LooseVersion('0.10')
        project_name = self.tracProject.service.project.name + '-' + self.tracProject.service.name
        db_str = 'sqlite:db/trac.db'
        if trac_version < v0_9: 
            db_str = '' # no db_str stuff in trac < 0.9
        repostype = 'svn'
        if trac_version < v0_10:
            repostype = '' # no repostype stuff in trac < 0.10
        templates_dir = self.dictionary['trac.templates_path']
        if trac_version > v0_10:
            templates_dir = '' # templates_dir in v0.11 onwards
        repository_dir = self.svnService.getDirPath()
        cmd = '%s initenv %s %s %s %s %s' % (
            self.tracadminBase, project_name, db_str, 
            repostype, repository_dir, templates_dir
        )
        status, output = commands.getstatusoutput(cmd)
        if status:
            msg = 'Creation of trac project environment failed'
            msg += '(cmd was: %s) (output was: %s)' % (cmd, output)
            self.raiseError(msg)

