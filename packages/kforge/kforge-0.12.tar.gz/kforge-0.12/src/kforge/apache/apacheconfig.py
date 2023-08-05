import commands

import dm.environment

from kforge.ioc import *
import kforge.url
import kforge.exceptions
import kforge.accesscontrol

class ApacheConfigBuilder(object):
    """
    Builds an Apache config file for KForge.
    Apache is a central component for KForge providing both a presentation
    layer as well as various services (dav, www, help with svn) and access
    control.
    
    Todo + Issues
    *************
    
    1. Do we support apache_ssl (as well as mod_ssl)? No at present.
    Shall we inherit PluginBase? It provides registry, dictionary, filesystem.
    
    Should we have build function here or in the plugin? If here we need to
    find a way to share that path info
    """
    
    registry      = RequiredFeature('DomainRegistry')
    fsPathBuilder = RequiredFeature('FileSystem')
    dictionary    = RequiredFeature('SystemDictionary')
    logger        = RequiredFeature('Logger')
    environment = dm.environment.SystemEnvironment(dictionary['system_name'])
    
    def __init__(self):
        self.vhostBuilder = VirtualHostBuilder()
        if self.dictionary['system_mode'] == 'production':
            self.pythonDebugMode = 'Off'
        else:
            self.pythonDebugMode = 'On'
        self.systemConfigEnvVarName = self.environment.getConfigFilePathEnvironmentVariableName()
        self.systemConfigFilePath = self.environment.getConfigFilePath()
    
    ## ********************************************************************
    ## Configuration Generation Methods
    ## ********************************************************************

    def reloadConfig(self):
        """Reload config into Apache.

        @return True on success, False on failure (but will log errors)
        """
        cmd = self.dictionary['www.reload_apache']
        if not cmd:
            if not self.dictionary['www.no_reload_apache']:
                msg = 'Not reloading apache, www.reload_apache not set.'
                self.logger.warning(msg)
            return True
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
        filePath = self.getConfigFilePath()
        configuration = self.getConfig()
        file = open(filePath, 'w')
        file.write(configuration)
        file.close()
        self.logger.info("Written new apache config to path: %s" % filePath)
    
    def getConfigFilePath(self):
        return self.dictionary['www.apache_config_file']
    
    def getConfig(self):
        """
        Get complete apache config file.
        This follows set up described in kforge.url
        
        @return: string which is apache config
        """
        result = self.getMediaHost()
        # default host automatically included in one of admin and project
        result += self.getAdminHostConfig()
        result += self.getProjectHostConfig()
        result = self.doVariableSubstitutionInString(result, self.dictionary)
        return result
    
    ## ********************************************************************
    ## Hosts
    ## ********************************************************************
    
    def getDefaultHostFragment(self):
        return  """
            # DEFAULT HOST STUFF
            ServerAlias ${domain_name} www.${domain_name}
            """
    
    def getMediaHost(self):
        hostFragment = 'DocumentRoot ' + self.dictionary['www.media_root']
        self.vhostBuilder.hostFragment = hostFragment
        self.vhostBuilder.serverName = self.dictionary['www.media_host']
        return self.vhostBuilder.getHttp() + self.vhostBuilder.getHttps()
    
    def getAdminHostConfig(self):
        urlBuilder = kforge.url.UrlBuilderAdmin()
        # runs off django so no doc root needed
        hostFragment = """
            SetEnv DJANGO_SETTINGS_MODULE kforge.django.settings.main
            SetHandler python-program
            PythonPath "'%s'.split(':') + sys.path"
            PythonHandler django.core.handlers.modpython
            PythonDebug %s
        """ % ( self.dictionary['pythonpath'], self.pythonDebugMode )
        if self.dictionary['address_scheme_default'] == 'admin':
            hostFragment = self.getDefaultHostFragment() + hostFragment
        self.vhostBuilder.hostFragment = hostFragment
        self.vhostBuilder.serverName = urlBuilder.getFqdn()
        return self.vhostBuilder.getHttp() + self.vhostBuilder.getHttps()
    
    def getProjectHostConfig(self):
        urlBuilder = kforge.url.UrlBuilderProject()
        hostFragment = """
            DocumentRoot %s
        """ % ( urlBuilder.getWebRoot(),
              )
        
        if self.dictionary['address_scheme_default'] == 'project':
            hostFragment = self.getDefaultHostFragment() + hostFragment
        
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
        if self.dictionary.has_key('www.project_vhost_fragment'):
            hostFragment += '''
            %s
            ''' % self.dictionary['www.project_vhost_fragment']
        
        self.vhostBuilder.hostFragment = hostFragment
        self.vhostBuilder.serverName = urlBuilder.getFqdn()
        return self.vhostBuilder.getHttp() + self.vhostBuilder.getHttps()
    
    ## ********************************************************************
    ## Helper Methods
    ## ********************************************************************
    
    def getPluginsCommonConfig(self):
        apacheConfigCommon = ''
        for plugin in self.registry.plugins:
            pluginSystem = plugin.getSystem()
            apacheConfigCommon += pluginSystem.getApacheConfigCommon()
        return '\n' + apacheConfigCommon
    
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
    
    def doVariableSubstitutionInString(self, inString, substitutionDictionary):
        varDict = substitutionDictionary
        keys = varDict.keys()
        for key in keys:
            value = varDict[key]
            # we match {key_value}, ${key_value} %(key_value)s
            # warning order matters
            keyTemplates = ['${' + key + '}', '{' + key + '}', '%('+ key +')s']
            for keyTemplate in keyTemplates:
                try:
                    inString = inString.replace(keyTemplate, str(value))
                except Exception, inst:
                    message = "Couldn't substitute value '%s' for variable '%s' in string '%s': %s" % (value, keyTemplate, inString, inst)
                    raise Exception(message)
        return inString
    
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

            # Use 'Satisfy any' with an AccessHandler and an AuthenHandler to
            # support login without 'Basic' prompt appearing. Handlers satisfy
            # the 'Satisfy any' condition when their method returns 0. The
            # first handler to return 0 is the last handler to be called.
            #
            # This pseduo-code describes the result of the config underneath:
            #
            #
            #    if accesshandler() == 0:         # Call AccessHandler
            #        return request.status        # Return if satisfied
            #                                     # No satisfaction yet
            #    popup_basic_auth_prompt()        # Apache raises popup
            #    if authenhandler() == 0:         # Call AuthenHandler
            #        return request.status        # Return if satisfied
            #                                     # No satisfaction yet
            #    return HTTP_FORBIDDEN            # Deny access
            #
            #   
            #    Satisfy any
            #    Require valid-user
            #    PythonAccessHandler myhandlers::accesshandler
            #    PythonAuthenHandler myhandlers::authenhandler
            #    AuthType Basic
            #    AuthName "Restricted Area"
            #
            #
            # That is, the 'Basic' password prompt is shown only when the
            # registered PythonAccessHandler does not return a 0 value. The
            # authenhandler is called after the password prompt is shown.
            #
            # To avoid the 'Basic' prompt, have the accesshandler return 0.
            #
            Satisfy any
            Require valid-user
            PythonAccessHandler kforge.handlers.projecthost::accesshandler
            PythonAuthenHandler kforge.handlers.projecthost::authenhandler
            AuthType Basic
            AuthName "%s Restricted Area"
            
            """ % (
                self.systemConfigEnvVarName,
                self.systemConfigFilePath,
                self.dictionary['pythonpath'],
                self.pythonDebugMode,
                self.dictionary['service_name'],
            )
            
        return modPythonAccessControl

    def canRead(self, service):
        return self.authoriseActionObject('Read', service)
        
    def canUpdate(self, service):
        return self.authoriseActionObject('Update', service)
        
    def authoriseActionObject(self, actionName, service):
        registry = RequiredFeature('DomainRegistry')
        person = registry.persons['visitor']
        accessControllerClass = kforge.accesscontrol.ProjectAccessController
        accessController = accessControllerClass(service.project)
        return accessController.isAuthorised(person, actionName, service.plugin)


class VirtualHostBuilder(object):

    dictionary = RequiredFeature('SystemDictionary')
    environment = dm.environment.SystemEnvironment(dictionary['system_name'])
    
    def __init__(self):
        self.hostFragment = ''
        self.serverName = ''
        self._virtualHost = """
        <VirtualHost %(ipAddress)s:%(port)s>
            ServerName %(serverName)s
            %(body)s
            %(env)s
            %(ssl)s
            %(logging)s
        </VirtualHost>
        """
    
    def getHttp(self):
        var = self.getVarDict()
        var['port'] = self.dictionary['www.port_http']
        var['ssl'] = ''
        return self._virtualHost % var 
    
    def getHttps(self):
        var = self.getVarDict()
        var['port'] = self.dictionary['www.port_https']
        return self._virtualHost % var
    
    def getVarDict(self):
        return {
            'ipAddress' : '${www.ip_address}',
            'serverName' : self.serverName,
            'body'    : self.hostFragment,
            'logging' : self.getLoggingFragment(),
            'ssl'     : self.getSslFragment(),
            'env'     : self.getEnvironmentVariables(),
        }
    
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
    
    def getLoggingFragment(self):
        logName = 'apache.' + self.serverName
        errorLogName = logName + '.error.log'
        customLogName = logName + '.log'
        apacheLogging = """
            # Logging
            ErrorLog ${logging.default_directory}/%s
            CustomLog ${logging.default_directory}/%s combined
        """ % (
            errorLogName,
            customLogName,
        )
        return apacheLogging
    
    def getSslFragment(self):
        return """
            # SSL
            <IfModule mod_ssl.c>
              SSLEngine on
              SSLCertificateFile ${www.ssl_certificate_file}
              SSLCertificateKeyFile ${www.ssl_certificate_key_file}
            </IfModule>
        """
