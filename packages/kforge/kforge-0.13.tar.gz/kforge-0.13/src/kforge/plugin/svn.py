"""
KForge Subversion plugin.
"""
import os
import commands
import shutil

import kforge.plugin.base
import kforge.utils.backup

class Plugin(kforge.plugin.base.ServicePlugin):
    "Subversion plugin."
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.utils = SvnUtils()
    
    def onServiceCreate(self, service):
        if service and service.plugin and service.plugin.name == 'svn':
            path = service.getDirPath()
            self.assertNotFileForPath(path)
            self.utils.createRepository(path)
            self.assertFileForPath(path)
            msg = 'SvnPlugin: Created service %s on path: %s)' % (
                service, path
            )
            self.log(msg)
    
    def onServicePurge(self, service):
        if service and service.plugin and service.plugin.name == 'svn':
            path = service.getDirPath()
            self.utils.deleteRepository(path)
            self.assertNotFileForPath(path)
            msg = 'SvnPlugin: Deleted service %s on path: %s' % (
                service, path
            )
            self.log(msg)
            
    def assertNotFileForPath(self, path):
        if os.path.exists(path):
            message = "Subversion repository exists on path: %s" % path
            self.logger.error(message)
            raise message

    def assertFileForPath(self, path):
        if not os.path.exists(path):
            message = "Subversion repository doesn't exist on path %s" % path
            self.logger.error(message)
            raise message
   
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
<p>This service provides a <a href="http://subversion.tigris.org/">subversion</a> repository located at:</p>
<p style="text-align: center"><a href="%(url)s">%(url)s</a></p>
<p>A subversion repository is a sharable versioned filesystem. To find out more about them see the <a href="http://svnbook.red-bean.com/">subversion book</a>. You can access the material in the repository in one of the following ways (provided you have read permissions):</p>
<ul>
    <li>Browse the material online by following the link to the subversion repository in your browser.</li>
    <li>'Check out' the repository with a suitable Subversion client. For example, if you are using the command line client, you would do:<br />
    <code>$ svn checkout %(url)s --username username</code><br /></li>
</ul>
<p>For more information on the command line client see the subversion book (chapter 3). Alternatively there is <a href="http://tortoisesvn.tigris.org/">Tortoise SVN</a>, a GUI client that integrates with Windows explorer. It has a <a href="http://tortoisesvn.net/doc_release">detailed manual</a> with chapter 5 covering 'daily use' -- checking out, committing etc.</p>
<p>Note that if you wish to 'commit' work to the repository you must have a role on the project that includes 'write' permissions on subversion services.</p>
'''

    def getUserHelp(self, service):
        serviceUrl = service.getUrl()
        values = { 'url' : serviceUrl }
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
        self.parentPath = parentPath
   
    # todo: remove this function: only used when parentPath != '' in test
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
        fullPath = self.getRepositoryPath(path)
        # cheap way to ensure parent directories exist (svn doesn't mind if
        # target directory exists as long as non-empty)
        if not os.path.exists(fullPath):
            os.makedirs(fullPath)
        type = 'fsfs'
        cmd = 'svnadmin create %s --fs-type %s' % (fullPath, type)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('svnadmin create error on %s: %s' % (cmd, output))

    def deleteRepository(self, path):
        """
        Destroys subversion repository file system.
        @path: see definition of path for createRepository
        """
        fullPath = self.getRepositoryPath(path)
        if os.path.exists(fullPath):
            shutil.rmtree(fullPath)

