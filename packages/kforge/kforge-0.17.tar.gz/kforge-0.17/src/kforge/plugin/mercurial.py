"""
KForge mercurial (hg) plugin.

Enabling this plugin allows users to create mercurial/hg services to provide
mercurial/hg repositories for their project.

## Installation ##

1. Dependencies. To create services using this plugin you must have installed
   the following external applications:

   * mercurial 

2. KForge config file. You can add the following (as stated this is optional):

[mercurial]
# optional -- if not specified the default hgweb_cgi (included in this module)
# will be used 
#
# NB: the strings "/path/to/repo" and "repository name" (including quotes!) will be
# replaced with correct values (if these strings exist)
hgweb.cgi-path = {path-to-your-cgi-file-template}

3. Install and enable this plugin in the usual way (see the KForge
   Documentation for details)
"""
import os
import commands
import shutil
from StringIO import StringIO
import tarfile

import kforge.plugin.base
import kforge.utils.backup
from kforge.dictionarywords import MERCURIAL_ADMIN_SCRIPT

class Plugin(kforge.plugin.base.ServicePlugin):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.utils = MercurialUtils(self.dictionary[MERCURIAL_ADMIN_SCRIPT])

    def checkDependencies(self):
        errors = []
        hgPath = self.dictionary[MERCURIAL_ADMIN_SCRIPT]
        cmd = 'which %s' % hgPath
        (status, output) = commands.getstatusoutput(cmd)
        if status:
            errors.append("Couldn't find Mercurial admin script '%s' on path." % hgPath)
        return errors

    def showDepends(self):
        hgPath = self.dictionary[MERCURIAL_ADMIN_SCRIPT]
        cmd = 'which %s' % hgPath
        (status, output) = commands.getstatusoutput(cmd)
        return [
            "Mercurial admin: %s" % (status and "Not found!" or ("Found OK. %s" % output)),
        ]

    showDepends = classmethod(showDepends)
    
    def onServiceCreate(self, service):
        if self.isOurs(service):
            self.assertServicesFolder(service)
            path = service.getDirPath()
            self.assertNotFileForPath(path)
            cgi_fo = StringIO(self.hgweb_cgi)
            service_name = service.project.name + '-' + service.name
            self.utils.create_with_web(path, cgi_fo, service_name)
            self.assertFileForPath(path)
            msg = 'MercurialPlugin: Created service %s on path: %s)' % (
                service, path
            )
            self.log(msg)
    
    def assertNotFileForPath(self, path):
        if os.path.exists(path):
            message = "Mercurial repository exists on path: %s" % path
            self.logger.error(message)
            raise Exception(message)

    def assertFileForPath(self, path):
        if not os.path.exists(path):
            message = "Mercurial repository doesn't exist on path %s" % path
            self.logger.error(message)
            raise Exception(message)
    
    def getApacheConfig(self, service):
        config = """
        # Follows
        # <http://www.selenic.com/mercurial/wiki/index.cgi/PublishingRepositories>
        #
        # ScriptAliasMatch in original but can just do simple ScriptAlias
        # ScriptAliasMatch ^%(urlPath)s(.*) %(fileSystemPath)s/hgweb.cgi$1
        ScriptAlias %(urlPath)s %(fileSystemPath)s/hgweb.cgi
        <Location %(urlPath)s>
            %(accessControl)s
        </Location>"""
        return config

    def backup(self, service, backupPathBuilder):
        path = service.getDirPath()
        backupPath = backupPathBuilder.getServicePath(service)
        self.utils.backup(path, backupPath)

    # From mercurial 0.9.5
    hgweb_cgi = \
'''#!/usr/bin/env python

# enable importing on demand to reduce startup time
from mercurial import demandimport; demandimport.enable()

# send python tracebacks to the browser if an error occurs:
import cgitb
cgitb.enable()

# If you'd like to serve pages with UTF-8 instead of your default
# locale charset, you can do so by uncommenting the following lines.
# Note that this will cause your .hgrc files to be interpreted in
# UTF-8 and all your repo files to be displayed using UTF-8.
#
import os
os.environ["HGENCODING"] = "UTF-8"

from mercurial.hgweb.hgweb_mod import hgweb
from mercurial.hgweb.request import wsgiapplication
import mercurial.hgweb.wsgicgi as wsgicgi

def make_web_app():
    return hgweb("/path/to/repo", "repository name")

wsgicgi.launch(wsgiapplication(make_web_app))
'''


class MercurialUtils(object):
   
    def __init__(self, adminScriptPath='hg'):
        self.adminScriptPath = adminScriptPath
 
    def create_with_web(self, path, cgi_fo, repo_name=''):
        '''Setup mercurial repo with web access.

        Repo is at path/repo and index.cgi is placed at path.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        repo_path = os.path.join(path, 'repo')
        self.create(repo_path)
        self.push_enable(repo_path)

        dest = os.path.join(path, 'hgweb.cgi')
        cgi_data = self.make_cgi(cgi_fo, repo_path, repo_name)
        fo = file(dest, 'w')
        fo.write(cgi_data)
        fo.close()
        # REALLY important make executable!
        os.chmod(dest, 0755)

    def make_cgi(self, cgi_fo, repo_path, repo_name):
        data = cgi_fo.read()
        data = data.replace('/path/to/repo', repo_path)
        data = data.replace('repository name', repo_name)
        return data
    
    def create(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        cmd = '%s init %s' % (self.adminScriptPath, path)
        status, output = commands.getstatusoutput(cmd)
        if status:
            raise Exception('mercurial create error on %s: %s' % (cmd, output))

    def push_enable(self, repopath):
        # Allowing Push in
        # <http://www.selenic.com/mercurial/wiki/index.cgi/PublishingRepositories>
        # Will use apache to restrict access not hg
        hgrc_path = os.path.join(repopath, '.hg', 'hgrc')
        fo = open(hgrc_path, 'w')
        fo.write(self.hgrc_text)
        fo.close()

    hgrc_text = \
'''
[web]
allow_push = *
# allow pushing over http as well as https 
push_ssl = false
'''

    def delete(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def backup(self, path, dest):
        dest = dest + '.tgz'
        tar = tarfile.open(dest, 'w:gz')
        tar.add(path)
        tar.close()

