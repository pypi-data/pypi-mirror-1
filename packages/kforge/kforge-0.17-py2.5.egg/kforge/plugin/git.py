"""KForge Git plugin.

Enabling this plugin allows KForge project administrators to create Git version control system services.

Creating services with this plugin requires:

  * Git. The 'git' command is used to create repositories (supplied by the 'git-core' package on Debian).

Providing access to this plugin's services requires:

  * Apache. The mod_python, and mod_dav Apache modules are used to provide access to Git through Apache. For example, on Debian the libapache2-mod-python and libapache2-svn packages must be installed and enabled.

Using Git repositories with Trac projects (optional) requires:

  * Trac's Git plugin. For example, on Debian the trac-git package can be installed.

You do not need to add anything to the KForge config file.

You can enable, disable, and show status in the usual way.

  $ kforge-admin plugin enable git
  $ kforge-admin plugin show git
  $ kforge-admin plugin disable git
"""
from kforge.dictionary import GIT_ADMIN_SCRIPT
import kforge.plugin.base
import os
import commands

class Plugin(kforge.plugin.base.ServicePlugin):
    
    def checkDependencies(self):
        errors = []
        path = self.dictionary[GIT_ADMIN_SCRIPT]
        cmd = 'which %s' % path
        (status, output) = commands.getstatusoutput(cmd)
        if status:
            errors.append("Couldn't find Git admin script '%s' on path." % path)
        return errors

    def showDepends(self):
        path = self.dictionary[GIT_ADMIN_SCRIPT]
        cmd = 'which %s' % path
        (status, output) = commands.getstatusoutput(cmd)
        return [
            "Git admin: %s" % (status and "Not found!" or ("Found OK. %s" % output)),
            "Apache dav module: %s" % "Please check this module is enabled.",
            "Apache dav_fs module: %s" % "Please check this module is enabled.",
            "Trac Git: %s" % "Please check this package is installed (optional).",
        ]
    showDepends = classmethod(showDepends)

    def onServiceCreate(self, service):
        if self.isOurs(service):
            servicePath = self.paths.getServicePath(service)
            msg = 'GitPlugin: Creating new Git repository for %s: %s' % (
                service, servicePath
            )
            self.logger.info(msg)
            self.paths.assertServiceFolder(service)
            self.createRepository(servicePath, self.dictionary[GIT_ADMIN_SCRIPT])

    def createRepository(self, path, gitCmd='git'):
        if not os.path.exists(path):
            os.makedirs(path)
        # Todo: Find out the correct command for git.
        cmd = 'cd %s; %s --bare init; git update-server-info; chmod +x hooks/post-commit' % (path, gitCmd)
        msg = 'GitPlugin: Initializing bare: %s' % cmd
        self.logger.info(msg)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('git create error on %s: %s' % (cmd, output))

    def getApacheConfigCommon(self):
        path = self.paths.getDavLockPath()
        return """
        # Follows
        # <http://www.kernel.org/pub/software/scm/git/docs/howto/setup-git-server-over-http.txt>
        DAVLockDB "%(davLockPath)s"
""" % {'davLockPath': path}

    def getApacheConfig(self, service):
        fsPath = self.paths.getServicePath(service)
        return """
        # Follows
        # <http://www.kernel.org/pub/software/scm/git/docs/howto/setup-git-server-over-http.txt>
        <Location %(urlPath)s>
            DAV On
#            Options +Indexes +FollowSymLinks
#            Allow from all
#            Order allow,deny
            %(accessControl)s
        </Location>
        Alias %(urlPath)s """ + fsPath + """
"""

    helpMessage = '''
<p>This service provides a <a href="http://git-scm.com/">Git</a> repository located at:</p>
<p style="text-align: center"><a href="%(url)s/">%(url)s/</a></p>
<p>A Git repository is a distributed version control system. To find out more about them see the <a href="http://git-scm.com/documentation">Git documentation</a>. You can access the material in the repository in one of the following ways (provided you have read permissions):</p>
<ul>
    <li>Browse the material online by following the link to the Git repository in your browser.</li>
    <li>'Clone' the repository with a suitable Git client. For example, if you are using the command line client, you would do:<br />
    <code>$ git clone %(url)s/</code><br /></li>
</ul>
<p>For more information on the command line client see the <a href="http://www.kernel.org/pub/software/scm/git/docs/user-manual.html#repositories-and-branches">Git Manual</a>. Alternatively there are GUIs for Git.
<p>Note that if you wish to 'push' work to the repository you must have a role on the project that includes 'write' permissions on Git services.</p>
<p>Then (as in <a href="http://www.kernel.org/pub/software/scm/git/docs/howto/setup-git-server-over-http.txt">this doc</a>)
add the following to your $HOME/.netrc:<br />
<code>machine &lt;servername&gt;<br />
login &lt;username&gt;<br />
password &lt;password&gt;<br />
</code></p>
<p>...and set permissions:<br />
<code>$ chmod 600 ~/.netrc</code></p>
<p>After adding changes and committing to the cloned repository, do<br />
<code>$ git push upload master</code></p>
<p>This pushes branch 'master' (which is assumed to be the branch you
want to export) to repository called 'upload', which we previously
defined with git-config.</p>
<p>To check whether all is OK, do:<br />
<code>curl --netrc --location -v http://<username>@<servername>/my-new-repo.git/HEAD</code></p>
<p>...this should give something like 'ref: refs/heads/master', which is
the content of the file HEAD on the server.</p>

'''


    def getUserHelp(self, service, serviceLocation):
        values = { 'url' : serviceLocation }
        msg = self.helpMessage % values
        return msg

