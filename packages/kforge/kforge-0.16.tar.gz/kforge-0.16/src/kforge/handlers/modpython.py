import os
from kforge.dictionarywords import *
from kforge.handlers.apachecodes import *
import Cookie

class ModPythonHandler(object):

    cookieClientIdentifiers = ['Mozilla', 'Links', 'Lynx', 'w3m'] 

    def __init__(self, request):
        self.request = request
        self.authuserName = ''
        self.application = None

    def authorise(self):
        self.initHandler()
        return DEFER_OR_DENY

    def initHandler(self):
        self.isAccessAllowed = False
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

    def initAuthuserNameFromDictionary(self):
        self.authuserName = self.application.dictionary[VISITOR_NAME]

    def validateRequestUri(self):
        return self.validateUri(self.request.uri)

    def validateUri(self, uri):
        "True if location has at least than two directories."
        path = self.normalizeUriPath(uri)
        if len(path.split('/')) < 2:
            self.logDebug('URI not validated: %s' % uri)
            return False
        else:
            self.logDebug('URI validiated: %s' % uri)
            return True
   
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

    def checkAccess(self):
        isAccessAllowed = False
        if self.application.debug:
            message = 'Checking access for: %s, %s, %s' % (
                self.authuserName,
                self.request.uri,
                self.request.method
            )
            self.logDebug(message)
        try:
            import kforge.apache.urlpermission as urlpermission
            isAccessAllowed = urlpermission.isAllowedAccess(
                self.authuserName,
                self.request.uri,
                self.request.method
            )
        except Exception, inst:
            if self.application.debug:
                message = 'Exception: %s' % str(inst)
                self.logDebug(message)
            raise
        if self.application.debug:
            if isAccessAllowed:
                message = "    ...allowing access."
                self.logDebug(message)
            else:
                message = "    ...not allowing access."
                self.logDebug(message)
        self.isAccessAllowed = isAccessAllowed
        return isAccessAllowed

    def logDebug(self, message):
        message = "%s handler: %s" % (
            self.__class__.__name__, 
            message
        )   
        self.application.logger.debug(message)

    def setRequestUser(self, userName):
        if type(userName) == unicode:
            userName = userName.encode('utf-8')
        if type(userName) != str:
            userName = str(userName)
        self.request.user = userName
        

class PythonAccessHandler(ModPythonHandler):

    def __init__(self, *args, **kwds):
        super(PythonAccessHandler, self).__init__(*args, **kwds)
        self.session = None

    def authorise(self):
        self.initHandler()
        if not self.validateRequestUri():
            return STOP_AND_DENY
        if self.isCookieClient():
            self.initAuthuserNameFromCookie()
            if self.checkAccess():
                if self.session:
                    # Setting request.user only under above conditions.
                    self.setRequestUser(self.authuserName)
                return STOP_AND_APPROVE
            else:
                self.setLoginRedirect()
                return STOP_AND_DENY
        else:
            self.initAuthuserNameFromDictionary()
            if self.checkAccess():
                return STOP_AND_APPROVE
            else:
                return DEFER_OR_DENY

    def initAuthuserNameFromCookie(self):
        self.authuserName = None
        authCookieValue = self.getAuthCookieValue()
        if authCookieValue:
            if self.application.debug:
                self.logDebug('Cookie: %s' % authCookieValue)
            import dm.view.base
            view = dm.view.base.ControlledAccessView(None)
            view.setSessionFromCookieString(authCookieValue)
            if view.session:
                self.session = view.session
                self.authuserName = self.session.person.name
            else:
                self.authuserName = self.application.dictionary[VISITOR_NAME]
        else:
            if self.application.debug:
                self.logDebug('No session cookie in request.')
            self.authuserName = self.application.dictionary[VISITOR_NAME]
        
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
            
    def setLoginRedirect(self):
        import kforge.url
        url_scheme = kforge.url.UrlScheme()
        if self.session:
            redirectUri = url_scheme.url_for_qualified('access_denied') 
            redirectUri += '/'
        else:
            redirectUri = url_scheme.url_for_qualified('login') 
            redirectUri += '/'
        current_uri = url_scheme.get_host() + self.request.uri
        redirectUri += current_uri
        self.request.err_headers_out.add('Location', redirectUri)
        if self.application.debug:
            self.logDebug('Redirecting to %s.' % redirectUri)
        self.request.status = HTTP_MOVED_TEMPORARILY


class PythonAuthenHandler(ModPythonHandler):

    def authorise(self):
        self.initHandler()
        if not self.validateRequestUri():
            return STOP_AND_DENY
        if self.isCookieClient():
            self.logDebug("Cookie clients shouldn't get here.")
            return STOP_AND_DENY
        self.initAuthuserNameFromBasicPrompt()
        if self.checkAccess():
            return STOP_AND_APPROVE
        else:
            return DEFER_OR_DENY

    def initAuthuserNameFromBasicPrompt(self):
        password = self.request.get_basic_auth_pw()
        if self.application.debug:
            msg = 'Running initAuthuserNameFromBasicPrompt.'
            msg += ' Current user is %s.' % self.request.user
            self.logDebug(msg)
        import kforge.apache.urlpermission as urlpermission
        self.authuserName = urlpermission.getVisitorName(
            self.request.user,
            password
        )

