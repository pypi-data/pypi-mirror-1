"""
KForge Trac plugin.

"""
import kforge.plugin.base
from kforge.plugin.trac.command import TracProjectEnvironmentCreate
from kforge.plugin.trac.command import AddAdminUserCommand
from kforge.plugin.trac.command import RemoveAdminUserCommand
from kforge.plugin.trac.command import IsAdminUserCommand
from kforge.plugin.trac.dom import TracProject
import os
# needed in order to get version
import trac

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
        return """
        Alias /trac %s
        """ % tracHtdocsPath
        
    def getApacheConfig(self, service):
        if not service or not service.name:
            return ""
        versionParts = trac.__version__.split('.')
        tracVersion = float(versionParts[0] + '.' + versionParts[1])
        modpythonHandler = ''
        if tracVersion <= 0.8:
            modpythonHandler = 'trac.ModPythonHandler'
        else:
            modpythonHandler = 'trac.web.modpython_frontend'
        urlBuilder = kforge.url.UrlBuilderAdmin() 
        logoutPath = 'http://%s/logout' % urlBuilder.getFqdn()
        result = 'Redirect %(urlPath)s/logout ' + logoutPath
        result += """
        <Location %(urlPath)s>
          <IfModule mod_python.c>
            SetHandler mod_python
            PythonHandler """
        result += modpythonHandler
        result += """
            PythonOption TracEnv %(fileSystemPath)s
            PythonOption TracUriRoot %(urlPath)s
            
            %(accessControl)s
          </IfModule>
        </Location>"""
        return result
    
    def backup(self, service, backupPathBuilder):
        backupPath = backupPathBuilder.getServicePath(service)
        os.system('trac-admin %s hotcopy %s' % (service.getDirPath(), backupPath))
