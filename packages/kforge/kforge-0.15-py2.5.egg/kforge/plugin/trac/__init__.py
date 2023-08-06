"""
KForge Trac plugin.

Installing this plugin allows users to create trac services to provide trac
installations associated with their project.

## Installation ##

1. To create services using this plugin you must have installed the following
   external applications:

   * trac
   * mod-python (this should already be installed for KForge itself to run)

2. KForge config file. Add the following to your KForge configuration file
   setting the variables as needed for your system::

[trac]
# path to trac templates
templates_path = /usr/share/trac/templates
# path to htdocs files
htdocs_path = /usr/share/trac/htdocs
# trac admin script
admin_script = trac-admin

3. Enable this plugin in the usual way (see the KForge Documentation for
   details)

4. [Optional] It is highly recommended that you also install the official
   WebAdmin trac plugin: <http://trac.edgewall.org/wiki/WebAdmin>. Full
   instructions can be found at that link (NB: as of trac v0.11 WebAdmin is
   part of trac core and therefore does not need to be separately installed).
   
   This allows users to administer most aspects of trac (trac specific
   permissions, template links, etc etc) from the web rather than needing
   access to the trac-admin command line utility.
"""
import os
import distutils.version
# import inline so that access to docstring works even when trac not installed
# import trac

import kforge.plugin.base
from kforge.plugin.trac.command import TracProjectEnvironmentCreate
from kforge.plugin.trac.command import AddAdminUserCommand
from kforge.plugin.trac.command import RemoveAdminUserCommand
from kforge.plugin.trac.command import IsAdminUserCommand
from kforge.plugin.trac.dom import TracProject

class Plugin(kforge.plugin.base.ServicePlugin):
    "Trac plugin."

    extendsDomainModel = True
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)

    def getRegister(self):
        domainClass = self.registry.getDomainClass('TracProject')
        return domainClass.createRegister(keyName='service')
    
    def onServiceCreate(self, service):
        if service and service.plugin and service.plugin.name == 'trac':
            try:
                self.register.create(service)
            except:
                service.delete()
                raise
            else:
                service.checkProjectPluginDir()
 
    def onTracProjectUpdate(self, tracProject):
        if tracProject.service and not tracProject.isEnvironmentInitialised:
            command = TracProjectEnvironmentCreate(tracProject)
            command.execute()
            for member in tracProject.service.project.members:
                if member.role.name == 'Administrator':
                    cmd = AddAdminUserCommand(tracProject, member.person.name)
                    cmd.execute()
    
    # [[TODO: enable (uncomment) this code so that trac subsystem permissions
    # track project permissions.
    # disabled for the time being because not yet under test]]
#    def onMemberUpdate(self, member):
#        if member.role.name == 'Administrator':
#            for service in member.project.services:
#                if service.plugin.name == 'trac':
#                    tracRegister = self.getRegister()
#                    tracProject = tracRegister[service]
#                    # be lazy and don't check whether already an admin
#                    # (errors only result in logged warning)
#                    cmd = AddAdminUserCommand(tracProject, member.person.name)
#                    cmd.execute()
#        else: # not an administrator
#            for service in member.project.services:
#                if service.plugin.name == 'trac':
#                    tracRegister = self.getRegister()
#                    tracProject = tracRegister[service]
#                    # be lazy and don't check whether already an admin
#                    # (errors only result in logged warning)
#                    cmd = RemoveAdminUserCommand(tracProject, member.person.name)
#                    cmd.execute()
#        
#    def onMemberDelete(self, member):
#        for service in member.project.services:
#            if service.plugin.name == 'trac':
#                tracRegister = self.getRegister()
#                tracProject = tracRegister[service]
#                # be lazy and don't check whether already an admin
#                # (errors only result in logged warning)
#                cmd = RemoveAdminUserCommand(tracProject, member.person.name)
#                cmd.execute()
    
    def onServicePurge(self, service):
        if service and service.plugin and service.plugin.name == 'trac':
            if service in self.register:
                tracProject = self.register[service]
                tracProject.service = None
                tracProject.svn = None
                tracProject.save()

    def listDependencies(self):
        dependencies = super(Plugin, self).listDependencies()
        dependencies.append('svn')
        return dependencies
        
    listDependencies = classmethod(listDependencies)

    def getMetaDomainObject(self):
        return TracProject.meta

    def getApacheConfigCommon(self):
        tracHtdocsPath = self.dictionary['trac.htdocs_path'] 
        # todo: Make the aliased location configurable, for versioning Trac.
        return """
        Alias /trac %s
        """ % tracHtdocsPath
        
    def getApacheConfig(self, service):
        if not service or not service.name:
            return ""
        import distutils
        # import inline so that access to docstring works
        import trac
        trac_version = distutils.version.LooseVersion(trac.__version__)
        v0_9 = distutils.version.LooseVersion('0.9')
        modpythonHandler = 'trac.web.modpython_frontend'
        if trac_version < v0_9:
            modpythonHandler = 'trac.ModPythonHandler'
        urlBuilder = kforge.url.UrlScheme() 
        logoutPath = urlBuilder.url_for_qualified('logout')
        result = 'Redirect %(urlPath)s/logout ' + logoutPath
        result += """
        <Location %(urlPath)s>
          <IfModule mod_python.c>
            SetHandler mod_python
            PythonHandler """
        result += modpythonHandler
        result += """
            PythonInterpreter main_interpreter
            PythonOption TracEnv %(fileSystemPath)s
            PythonOption TracUriRoot %(urlPath)s
            
            %(accessControl)s
          </IfModule>
        </Location>"""
        return result
    
    def backup(self, service, backupPathBuilder):
        backupPath = backupPathBuilder.getServicePath(service)
        os.system('trac-admin %s hotcopy %s' % (service.getDirPath(), backupPath))
