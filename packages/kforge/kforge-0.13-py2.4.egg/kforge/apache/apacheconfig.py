"""
To use apacheconfig open up the virtual host where you would like to install
kforge and add to it the line:

    Include <kforge-http-config-path>

where <kforge-http-config-path> is the path set in the your KForge config for
the variable named 'apache_config_file'.

Question: do we support `multi-vhost' setups?
"""
from kforge.exceptions import MissingPluginSystem
from kforge.dictionarywords import SYSTEM_NAME
from kforge.ioc import *
import dm.environment
import kforge.accesscontrol
import dm.environment
import kforge.url
import commands

class ApacheConfigBuilder(object):
    """
    Builds an Apache configuration needed for KForge.

    Apache is a central component for KForge providing both a presentation
    layer as well as various services (dav, www, help with svn) and access
    control.
    """
    
    registry      = RequiredFeature('DomainRegistry')
    fsPathBuilder = RequiredFeature('FileSystem')
    dictionary    = RequiredFeature('SystemDictionary')
    logger        = RequiredFeature('Logger')
    environment = dm.environment.SystemEnvironment(dictionary[SYSTEM_NAME])
    
    def __init__(self):
        if self.dictionary['system_mode'] == 'production':
            self.pythonDebugMode = 'Off'
        else:
            self.pythonDebugMode = 'On'
        self.systemConfigEnvVarName = self.environment.getConfigFilePathEnvironmentVariableName()
        self.systemConfigFilePath = self.environment.getConfigFilePath()
        self.url_scheme = kforge.url.UrlScheme()
    
    ## ********************************************************************
    ## Configuration Generation Methods
    ## ********************************************************************

    def reloadConfig(self):
        """Reload config into Apache.

        @return True on success, False on failure (but will log errors)
        """
        if self.dictionary['www.no_reload_apache']:
            msg = 'Not reloading apache, www.no_reload_apache is set.'
            self.logger.warning(msg)
            return True
        cmd = self.dictionary['www.reload_apache']
        try:
            errorStatus, output = commands.getstatusoutput(cmd)
            if errorStatus:
                msg = 'Failed to reload apache with [%s]: %s' % (cmd, output)
                self.logger.error(msg)
                return False
            return True
        except Exception, inst:
            self.logger.error('Exception on reload of apache: %s' % inst)
            return False

    def buildConfig(self):
        """
        Recreates configuration and writes to file.
        """
        filePath = self.dictionary['www.apache_config_file']
        configuration = self.getConfig()
        file = open(filePath, 'w')
        file.write(configuration)
        file.close()
        self.logger.info("Written new apache config to path: %s" % filePath)
    
    def getConfig(self):
        """
        Get apache config file.
        This follows set up described in kforge.url
        
        @return: string which is apache config
        """
        result = self.getMediaHost()
        result += self.getAdminHostConfig()
        result += self.getProjectHostConfig()
        return result
    
    ## ********************************************************************
    ## Hosts
    ## ********************************************************************
    
    def getMediaHost(self):
        url_path = self.url_scheme.media_path()
        media_path = self.dictionary['www.media_root']
        frag = '''
        Alias %s %s
        ''' % (url_path, media_path)
        return frag
    
    def getDjangoHandledPaths(self):
        admin_paths = ''
        admin_paths += '^%s$' % self.url_scheme.url_for('home')
        extra_paths = [
                self.url_scheme.url_for('person'),
                self.url_scheme.url_for('project'),
                self.url_scheme.url_for('admin'),
                self.url_scheme.url_for('login'),
                self.url_scheme.url_for('logout'),
                ]
        for path in extra_paths:
            admin_paths += '|^%s($|/.*)' % path
        return admin_paths

    def getAdminHostConfig(self):
        handled_paths = self.getDjangoHandledPaths()
        hostFragment = """
        ## *********************************************************
        ## STARTING Kforge 'Django' section 
        ## *********************************************************

        # Use LocationMatch rather than just <Location />
        # because o/w modpython handler will handle all requests
        # (Even where you have Alias /... 
        <LocationMatch "%s" >
            %s
            SetHandler python-program
            PythonInterpreter kforge_interpreter
            PythonPath "'%s'.split(':') + sys.path"
            PythonHandler django.core.handlers.modpython
            PythonDebug %s
        </LocationMatch>

        ## *********************************************************
        ## ENDING Kforge 'Django' section 
        ## *********************************************************
        """ % ( handled_paths,
                self.getEnvironmentVariables(),
                self.dictionary['pythonpath'],
                self.pythonDebugMode )
        return hostFragment
    
    def getProjectHostConfig(self):
        urlBuilder = kforge.url.UrlScheme()
        hostFragment = '''
        ## *********************************************************
        ## STARTING Kforge Project Services section ...
        ## *********************************************************
        '''
        hostFragment += self.getEnvironmentVariables()
        hostFragment += self.getPluginsCommonConfig()
        for project in self.registry.projects:
            # have to www last because it is at the base project url which 
            # means it Alias command must come last
            for service in project.services:
                if service.plugin.name != 'www':
                    hostFragment += self.getServiceSection(urlBuilder, service)
            for service in project.services:
                if service.plugin.name == 'www':
                    hostFragment += self.getServiceSection(urlBuilder, service)
        hostFragment += '''
        ## *********************************************************
        ## ENDING KForge Project Services section ...
        ## *********************************************************
        '''
        return hostFragment
        
    
    ## ********************************************************************
    ## Helper Methods
    ## ********************************************************************
    
    def getEnvironmentVariables(self):
        systemConfigEnvVarName = self.environment.getConfigFilePathEnvironmentVariableName()
        systemConfigFilePath = self.environment.getConfigFilePath()
        return """
            # Set environment
            # Need to set DJANGO as used in both project (auth) and admin
            SetEnv DJANGO_SETTINGS_MODULE kforge.django.settings.main
            SetEnv %s %s
            SetEnv PYTHONPATH %s
        """ % (
            systemConfigEnvVarName,
            systemConfigFilePath,
            self.dictionary['pythonpath']
        )
    
    def getPluginsCommonConfig(self):
        configSnippet = ''
        for plugin in self.registry.plugins:
            pluginSystem = plugin.getSystem()
            if pluginSystem:
                configSnippet += pluginSystem.getApacheConfigCommon()
            else:
                msg = "No '%s' plugin system from which to build apache config." % (
                    plugin.name
                )
                self.logger.error(msg)
                raise MissingPluginSystem(msg)
        return '\n' + configSnippet
    
    def getServiceSection(self, urlBuilder, service):
        "Generates Apache config fragment for service."
        if not service.plugin:
            msg = "No apache config without plugin on service: %s" % service
            self.logger.warning(msg)
            return "\n# %s\n" % msg
        pluginSystem = service.plugin.getSystem()
        apacheConfigTemplate = pluginSystem.getApacheConfig(service)
        varDict = {}
        varDict['urlPath'] = urlBuilder.getServicePath(service)
        varDict['fileSystemPath'] = self.fsPathBuilder.getServicePath(service)
        varDict['accessControl'] = self.getAccessControl(service)
        return '\n' + apacheConfigTemplate % varDict
    
    def getAccessControl(self, service):
        """
        Get access control fragment.
        """
        return self.getModPythonAccessControl()

    def getModPythonAccessControl(self):
        modPythonAccessControl = """
            # Need to set DJANGO as used in both project (auth) and admin
            # Set as PYTHONOPTION as SetEnv does not seem to work in here
            PYTHONOPTION DJANGO_SETTINGS_MODULE kforge.django.settings.main
            PYTHONOPTION %s %s
            PythonPath "'%s'.split(':') + sys.path"
            PythonDebug %s

            # For details see comments in kforge.handlers.projecthost.py
            Satisfy any
            PythonAccessHandler kforge.handlers.projecthost::accesshandler
            PythonAuthenHandler kforge.handlers.projecthost::authenhandler
            AuthType basic
            AuthUserFile /dev/null
            AuthName "%s Restricted Area"
            Require valid-user
            # Only available in mod_auth_basic available in apache >= 2.1
            <IfModule mod_auth_basic.c>
                AuthBasicAuthoritative Off
            </IfModule>
            """ % (
                self.systemConfigEnvVarName,
                self.systemConfigFilePath,
                self.dictionary['pythonpath'],
                self.pythonDebugMode,
                self.dictionary['service_name'],
            )
            
        return modPythonAccessControl

