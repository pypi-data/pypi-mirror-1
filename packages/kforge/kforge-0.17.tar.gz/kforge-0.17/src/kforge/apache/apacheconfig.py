"""
To use apacheconfig open up the virtual host where you would like to install
kforge and add to it the line:

    Include <kforge-http-config-path>

where <kforge-http-config-path> is the path set in the your KForge config for
the variable named 'apache_config_file'.

Question: do we support `multi-vhost' setups?
"""
from dm.apache.config import ApacheConfigBuilder
from kforge.exceptions import MissingPluginSystem
from kforge.ioc import *
import dm.environment
import kforge.accesscontrol
import dm.environment
import kforge.url
import commands

class ApacheConfigBuilder(ApacheConfigBuilder):
    """
    Builds an Apache configuration needed for KForge.

    Apache is a central component for KForge providing both a presentation
    layer as well as various services (dav, www, help with svn) and access
    control.
    """
    
    registry = RequiredFeature('DomainRegistry')
    fsPathBuilder = RequiredFeature('FileSystem')
    
    def __init__(self):
        super(ApacheConfigBuilder, self).__init__()
        self.url_scheme = kforge.url.UrlScheme()
    
    ## ********************************************************************
    ## Configuration Generation Methods
    ## ********************************************************************

    def createConfigContent(self):
        """
        Follows set up described in kforge.url.
        """
        mediaHostConfig = self.getMediaHost()
        adminHostConfig = self.getAdminHostConfig()
        projectHostConfig = self.getProjectHostConfig()
        configContent = mediaHostConfig + adminHostConfig + projectHostConfig
        return configContent
    
    ## ********************************************************************
    ## Hosts
    ## ********************************************************************

    # todo: Check whether this stuff is really to do with 'hosts' still...
    
    def getMediaHost(self):
        urlPath = self.url_scheme.media_path()
        mediaPath = self.dictionary[self.dictionary.words.MEDIA_PATH]
        frag = '''
        Alias %s %s
        ''' % (urlPath, mediaPath)
        return frag
    
    def getDjangoHandledPaths(self):
        adminPaths = ''
        adminPaths += '^%s$' % self.url_scheme.url_for('home')
        extraPaths = [
                self.url_scheme.url_for('feed'),
                self.url_scheme.url_for('access_denied'),
                self.url_scheme.url_for('login'),
                self.url_scheme.url_for('logout'),
                self.url_scheme.url_for('admin'),
                self.url_scheme.url_for('person'),
                self.url_scheme.url_for('project'),
                ]
        for path in extraPaths:
            adminPaths += '|^%s($|/.*)' % path
        return adminPaths

    def getAdminHostConfig(self):
        handledPaths = self.getDjangoHandledPaths()
        if self.dictionary[self.dictionary.words.VIRTUALENVBIN_PATH]:
            djangoHandlerName = 'kforgevirtualenvhandlers::djangohandler'
        else:
            djangoHandlerName = 'django.core.handlers.modpython'
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
            PythonPath "'%s'.split(':') + sys.path"
            PythonHandler %s
            PythonDebug %s
        </LocationMatch>

        ## *********************************************************
        ## ENDING Kforge 'Django' section 
        ## *********************************************************
        """ % ( handledPaths,
                self.getEnvironmentVariables(),
                self.dictionary[self.dictionary.words.PYTHONPATH],
                djangoHandlerName,
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
            self.dictionary[self.dictionary.words.PYTHONPATH]
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
        uriPrefix = self.dictionary[self.dictionary.words.URI_PREFIX]
        serviceUrl = urlBuilder.getServicePath(service)
        serviceUrlNoPrefix = serviceUrl.replace(uriPrefix, '', 1)
        varDict = {}
        varDict['urlPath'] = serviceUrl
        varDict['urlPathNoPrefix'] = serviceUrlNoPrefix
        varDict['fileSystemPath'] = self.fsPathBuilder.getServicePath(service)
        varDict['accessControl'] = self.getAccessControl(service)
        return '\n' + apacheConfigTemplate % varDict
    
    def getAccessControl(self, service):
        """
        Get access control fragment.
        """
        return self.getModPythonAccessControl()

    def getModPythonAccessControl(self):
        if self.dictionary[self.dictionary.words.VIRTUALENVBIN_PATH]:
            accessHandlerName = 'kforgevirtualenvhandlers::accesshandler'
            authenHandlerName = 'kforgevirtualenvhandlers::authenhandler'
        else:
            accessHandlerName = 'kforge.handlers.projecthost::accesshandler'
            authenHandlerName = 'kforge.handlers.projecthost::authenhandler'
        modPythonAccessControl = """
            # Need to set DJANGO as used in both project (auth) and admin
            # Set as PYTHONOPTION as SetEnv does not seem to work in here
            PYTHONOPTION DJANGO_SETTINGS_MODULE kforge.django.settings.main
            PYTHONOPTION %s %s
            PythonPath "'%s'.split(':') + sys.path"
            PythonDebug %s

            # For details see comments in kforge.handlers.projecthost.py
            Satisfy any
            PythonAccessHandler %s
            PythonAuthenHandler %s
            AuthType basic
            AuthName "%s Restricted Area"
            Require valid-user
            # Only available in mod_auth_basic available in apache >= 2.1
            <IfModule mod_auth_basic.c>
                AuthBasicAuthoritative Off
                AuthUserFile /dev/null
            </IfModule>
            """ % (
                self.systemConfigEnvVarName,
                self.systemConfigFilePath,
                self.dictionary[self.dictionary.words.PYTHONPATH],
                self.pythonDebugMode,
                accessHandlerName,
                authenHandlerName,
                self.dictionary[self.dictionary.words.SYSTEM_SERVICE_NAME].decode('utf-8'),
            )
            
        return modPythonAccessControl
