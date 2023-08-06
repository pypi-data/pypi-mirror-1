"""KForge Subversion Plugin

Enabling this plugin allows KForge project administrators to create Subversion version control system services.

Creating services with this plugin requires:

  * Subversion. The 'svnadmin' command is used to create repositories.

Providing access to this plugin's services requires:

  * Apache. The mod_python, mod_dav, mod_dav_fs, and mod_dav_svn Apache modules are used to provide access to Subversion through Apache. For example, on Debian the libapache2-mod-python and libapache2-svn packages must be installed and enabled.

You do not need to add anything to the KForge config file.

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable svn
  $ kforge-admin plugin show svn
  $ kforge-admin plugin disable svn
"""
import os
import commands
import shutil

import kforge.plugin.base
import kforge.utils.backup
from kforge.dictionary import SVN_ADMIN_SCRIPT

class Plugin(kforge.plugin.base.ServicePlugin):
    "Subversion plugin."
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.utils = SvnUtils()
   
    def checkDependencies(self):
        errors = []
        svnadminPath = self.dictionary[SVN_ADMIN_SCRIPT]
        cmd = 'which %s' % svnadminPath
        (status, output) = commands.getstatusoutput(cmd) 
        if status:
            errors.append("Couldn't find Subversion admin script '%s' on path." % svnadminPath)
        return errors

    def showDepends(self):
        svnadminPath = self.dictionary[SVN_ADMIN_SCRIPT]
        cmd = 'which %s' % svnadminPath
        (status, output) = commands.getstatusoutput(cmd) 
        return [
            "Subversion admin: %s" % (status and "Not found!" or ("Found OK. %s" % output)),
            "Apache dav module: %s" % "Please check this module is enabled.",
            "Apache dav_fs module: %s" % "Please check this module is enabled.",
            "Apache dav_svn module: %s" % "Please check this module is enabled.",
        ]
    showDepends = classmethod(showDepends)
 
    def onServiceCreate(self, service):
        if self.isOurs(service):
            servicePath = self.paths.getServicePath(service)
            msg = 'SvnPlugin: Creating new Subversion repository for %s: %s' % (
                service, servicePath
            )
            self.logger.info(msg)
            self.paths.assertServiceFolder(service)
            self.utils.createRepository(servicePath)
    
    def getApacheConfig(self, service):
        config = """
        <Location %(urlPath)s>
          <IfModule mod_dav.c>
            DAV svn 
            SVNPath %(fileSystemPath)s
            %(accessControl)s
          </IfModule>
        </Location>"""
        return config

    helpMessage = '''
<p>This service provides a <a href="http://subversion.tigris.org/">Subversion</a> repository located at:</p>
<p style="text-align: center"><a href="%(url)s">%(url)s</a></p>
<p>A Subversion repository is a sharable versioned filesystem. To find out more about them see the <a href="http://svnbook.red-bean.com/">Subversion book</a>. You can access the material in the repository in one of the following ways (provided you have read permissions):</p>
<ul>
    <li>Browse the material online by following the link to the Subversion repository in your browser.</li>
    <li>'Check out' the repository with a suitable Subversion client. For example, if you are using the command line client, you would do:<br />
    <code>$ svn checkout %(url)s --username username</code><br /></li>
</ul>
<p>For more information on the command line client see the Subversion book (chapter 3). Alternatively there is <a href="http://tortoisesvn.tigris.org/">Tortoise SVN</a>, a GUI client that integrates with Windows explorer. It has a <a href="http://tortoisesvn.net/doc_release">detailed manual</a> with chapter 5 covering 'daily use' -- checking out, committing etc.</p>
<p>Note that if you wish to 'commit' work to the repository you must have a role on the project that includes 'write' permissions on Subversion services.</p>
'''

    def getUserHelp(self, service, serviceLocation):
        values = { 'url' : serviceLocation }
        msg = self.helpMessage % values
        return msg
    
    def backup(self, service, backupPathBuilder):
        backupPath = backupPathBuilder.getServicePath(service)
        backupItem = kforge.utils.backup.BackupItemSvn(
            backupPath, '', service.getDirPath()
        )
        backupItem.doBackup()


class SvnUtils(object):
    
    def __init__(self, parentPath = ''):
        """
        @parentPath: string representing parent path to use when creating
                     repositories. If not defined then defaults to empty string
                     (so repositories must be specified with their path)
        """
        # NB: Only used in svntest.py.
        # Todo: Move test path switching to dictionary manipulations?
        self.parentPath = parentPath  
   
    # NB: Only used when parentPath != '' in test.
    # Todo: Remove this function, it's distracting. :-)
    def getRepositoryPath(self, name):
        "Returns file system path from repository name."
        path = os.path.join(self.parentPath, name)
        return path
    
    def createRepository(self, path):
        """
        Creates repository with correct permissions.
        @path: a path to use for repository creation. If absolute it is used on 
               its own and if relative it is joined to parentPath defined at
               creation of class.
        """
        path = self.getRepositoryPath(path)
        type = 'fsfs'
        cmd = 'svnadmin create %s --fs-type %s' % (path, type)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('Subversion command error: %s: %s' % (cmd, output))

    def deleteRepository(self, path):
        """
        Destroys Subversion repository file system.
        @path: see definition of path for createRepository
        """
        fullPath = self.getRepositoryPath(path)
        if os.path.exists(fullPath):
            shutil.rmtree(fullPath)

