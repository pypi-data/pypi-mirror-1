import os
from kforge.dictionarywords import *
from kforge.handlers.apachecodes import *
from kforge.command import PersonRead
from kforge.url import UrlScheme
from kforge.exceptions import KforgeRegistryKeyError
import Cookie
import traceback

class ModPythonHandler(object):
    """
    Responsible for authentication and access control based upon session
    cookies, and for redirecting to the KForge login page or deferring control
    to the authen handler if access is not allowed, for clients which do 
    support cookies (such as Mozilla, Lynx, etc.).

    """

    cookieClientIdentifiers = ['Mozilla', 'Links', 'Lynx', 'w3m'] 

    def __init__(self, request):
        self.request = request
        self.authuser = None
        self.application = None

    def authorise(self):
        try:
            self.initHandler()
            message = 'Handling access control check: %s %s' % (
                self.request.method,
                self.request.uri,
            )
            self.logInfo(message)
            modpythonStatus = self.authoriseRequest()
        except Exception, inst:
            msg = "Failed to complete authorise() method: %s\n" % repr(inst)
            msg += traceback.format_exc()
            self.logError(msg)
            # Todo: Redirect with an error message to 'sorry' page.
            if self.isCookieClient():
                self.request.err_headers_out.add('Location', '/')
                self.request.status = HTTP_MOVED_TEMPORARILY
                self.request.write("\n")
            modpythonStatus = DONE
        self.logInfo('Returning code (%s) to mod_python.' % modpythonStatus)
        return modpythonStatus

    def initHandler(self):
        self.accessStatus = False
        self.initEnviron()
        self.initApplication()
        self.request.add_common_vars()

    def initEnviron(self):
        # Set environ from configured request options (SetEnv doesn't work).
        systemSettingsPath = self.request.get_options()['KFORGE_SETTINGS']  
        os.environ['KFORGE_SETTINGS'] = systemSettingsPath
        djangoSettingsName=self.request.get_options()['DJANGO_SETTINGS_MODULE']
        os.environ['DJANGO_SETTINGS_MODULE'] = djangoSettingsName

    def initApplication(self):
        import kforge.soleInstance
        self.application = kforge.soleInstance.application

    def authoriseRequest(self):
        return DEFER_OR_DENY

    def validateRequestUri(self):
        return self.validateUri(self.getRequestUri())

    def isLoginUri(self):
        urlPath = self.normalizeUriPath(self.getRequestUri())
        return 'login' in urlPath.split('/')[-1]

    def isLogoutUri(self):
        urlPath = self.normalizeUriPath(self.getRequestUri())
        return 'logout' in urlPath.split('/')[-1]

    def getRequestUri(self):
        return self.request.uri

    def validateUri(self, uri):
        "True if location has at least one directories."
        # Todo: This method effectively only invalidates a '/'. Make clear?
        uri = self.normalizeUriPath(uri)
        if len(uri.split('/')) >= 2:
            self.logDebug('%s: Valid request path: %s' % (
                self.__class__.__name__, uri))
            return True
        else:
            self.logInfo('%s: Invalid request path: %s' % (
                self.__class__.__name__, uri))
            return False
   
    def normalizeUriPath(self, uri):
        "Removes trailing slash."
        if uri[-1] == '/':
            uri = uri[:-1]
        return uri

    def isCookieClient(self):
        "True if client supports cookies and redirection."
        user_agent = self.request.subprocess_env.get('HTTP_USER_AGENT', '')
        isCookieClient = False
        for identifier in self.cookieClientIdentifiers:
            if identifier in user_agent:
                isCookieClient = True
                break
        if self.application.debug:
            if isCookieClient:
                self.logDebug('Cookie client making request.')
            else:
                self.logDebug('Basic client making request.')
            self.logDebug('User-Agent: %s' % user_agent)
        return isCookieClient

    def isAccessAuthorised(self):
        self.accessStatus = False
        uri = self.normalizeUriPath(self.getRequestUri())
        service = self.getServiceFromUri(uri)
        if service:
            actionName = self.getActionName()
            self.accessStatus = self.application.accessController.isAuthorised(
                person=self.authuser,
                actionName=actionName,
                protectedObject=service.plugin,
                project=service.project,
            )
        return self.accessStatus

    def getActionName(self):
        readList = ['GET', 'PROPFIND', 'OPTIONS', 'REPORT']
        if self.request.method in readList:
            return 'Read'
        else:
            return 'Update'

    def getServiceFromUri(self, uri):
        (projectName, serviceName) = UrlScheme().decodeServicePath(uri)
        try:
            project = self.application.registry.projects[projectName]
        except KforgeRegistryKeyError:
            return None
        try:
            service = project.services[serviceName]
        except KforgeRegistryKeyError:
            return None
        return service

    def logInfo(self, message):
        message = "%s: %s" % (
            self.__class__.__name__, 
            message
        )   
        self.application.logger.info(message)

    def logDebug(self, message):
        message = "%s: %s" % (
            self.__class__.__name__, 
            message
        )   
        self.application.logger.debug(message)

    def logError(self, message):
        message = "%s: %s" % (
            self.__class__.__name__, 
            message
        )   
        self.application.logger.error(message)

    def initAuthuserFromDictionary(self):
        read = PersonRead(self.application.dictionary[VISITOR_NAME])
        read.execute()
        self.authuser = read.person


class PythonAccessHandler(ModPythonHandler):
    """
    Responsible for authentication of and access control based upon
    credentials supplied through the 'Basic' password prompt for clients
    which don't support cookies (such as DAV, SVN, etc.).
    
    """

    def __init__(self, *args, **kwds):
        super(PythonAccessHandler, self).__init__(*args, **kwds)
        self.session = None

    def authoriseRequest(self):
        if self.isCookieClient():
            if not self.validateRequestUri():
                self.setRedirect()
                return DONE
            elif self.isLoginUri():
                self.setRedirect('login')
                return DONE
            elif self.isLogoutUri():
                self.setRedirect('logout')
                return DONE
            self.initAuthuserFromCookie()
            if self.isAccessAuthorised():
                if self.session:
                    # Set request.user only under above conditions.
                    self.setRequestUser(self.authuser.name)
                return STOP_AND_APPROVE
            else:
                self.setRedirect()
                return DONE
        else:
            if not self.validateRequestUri():
                return DONE
            self.initAuthuserFromDictionary()
            if self.isAccessAuthorised():
                return STOP_AND_APPROVE
            else:
                return DEFER_OR_DENY

    def initAuthuserFromCookie(self):
        self.authuser = None
        authCookieValue = self.getAuthCookieValue()
        if authCookieValue:
            if self.application.debug:
                self.logDebug('Cookie: %s' % authCookieValue)
            import dm.view.base
            view = dm.view.base.ControlledAccessView(None)
            view.setSessionFromCookieString(authCookieValue)
            if view.session:
                self.session = view.session
                self.authuser = self.session.person
            else:
                self.initAuthuserFromDictionary()
        else:
            if self.application.debug:
                self.logDebug('No session cookie in request.')
            self.initAuthuserFromDictionary()
        
    def setRequestUser(self, userName):
        if type(userName) == unicode:
            userName = userName.encode('utf-8')
        if type(userName) != str:
            userName = str(userName)
        self.request.user = userName
        
    def getAuthCookieValue(self):
        authCookieName = self.application.dictionary[AUTH_COOKIE_NAME]
        return self.getCookieValue(authCookieName)

    def getCookieValue(self, cookieName):
        "Retrieves named cookie."
        headers_in = self.request.headers_in
        if headers_in.has_key('Cookie'):
            rawCookie = headers_in['Cookie']
            cookies = Cookie.SimpleCookie()
            cookies.load(rawCookie)
            if cookies.has_key(cookieName):
                return cookies[cookieName].value
        return ''
            
    def setRedirect(self, locationName=None):
        try:
            import kforge.url
            urlScheme = kforge.url.UrlScheme()
            if not locationName:
                if self.session:
                    locationName = 'access_denied'
                else:
                    locationName = 'login'
            pageUri = urlScheme.url_for(locationName) 
            if pageUri[-1] != '/':
                pageUri += '/'
            redirectUri = pageUri
            currentUri = self.request.uri
            if currentUri[-1] != '/':
                currentUri += '/'
            # Return to parent of a login page.
            currentUri = currentUri.replace('/login', '')
            redirectUri += "?returnPath=%s" % currentUri  
            self.logInfo('Redirecting to %s.' % redirectUri)
            self.request.err_headers_out.add('Location', redirectUri)
            self.request.status = HTTP_MOVED_TEMPORARILY
            self.request.write("\n")
        except Exception, inst:
            msg = "Couldn't set redirect: %s" % repr(inst)
            self.logError(msg)


class PythonAuthenHandler(ModPythonHandler):

    def authoriseRequest(self):
        if not self.validateRequestUri():
            return STOP_AND_DENY
        if self.isCookieClient():
            self.logDebug("Cookie clients shouldn't get here.")
            return STOP_AND_DENY
        self.initAuthuserFromBasicPrompt()
        if self.isAccessAuthorised():
            return STOP_AND_APPROVE
        else:
            return DEFER_OR_DENY

    def initAuthuserFromBasicPrompt(self):
        password = self.request.get_basic_auth_pw()
        if self.application.debug:
            msg = 'Running initAuthuserFromBasicPrompt.'
            msg += ' Current user is %s.' % self.request.user
            self.logDebug(msg)
        import kforge.apache.urlpermission as accessController
        personName = self.request.user
        self.authuser = accessController.isAuthenticated(personName, password)
        if not self.authuser:
            self.initAuthuserFromDictionary()
