import os
from kforge.dictionarywords import *
from kforge.handlers.apachecodes import *
import Cookie

class ModPythonHandler(object):

    cookieClientIdentifiers = ['Mozilla', 'Links', 'Lynx', 'w3m'] 
    app = None

    def __init__(self, request):
        self.request = request

    def authorise(self):
        self.initHandler()
        return HTTP_UNAUTHORIZED

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
        self.app = kforge.soleInstance.application

    def initAuthuserNameFromDictionary(self):
        self.authuserName = self.app.dictionary[VISITOR_NAME]
        self.request.user = self.authuserName

    def validateRequestUri(self):
        return self.validateUri(self.request.uri)

    def validateUri(self, uri):
        "True if location has at least than two directories."
        path = self.normalizeUriPath(uri)
        if len(path.split('/')) < 2:
            self.loggerDebug('URI not validated: %s' % uri)
            return False
        else:
            self.loggerDebug('URI validiated: %s' % uri)
            return True
   
    def normalizeUriPath(self, uri):
        "Removes trailing slash."
        if uri[-1] == '/':
            uri = uri[:-1]
        return uri

    def isCookieClient(self):
        "True if client supports cookies and redirection."
        http_user_agent = self.request.subprocess_env.get('HTTP_USER_AGENT', '')
        isCookieClient = False
        for identifier in self.cookieClientIdentifiers:
            if identifier in http_user_agent:
                isCookieClient = True
                break
        if self.app.debug:
            if isCookieClient:
                self.loggerDebug('Cookie client making request.')
            else:
                self.loggerDebug('Basic client making request.')
            self.loggerDebug('User-Agent: %s' % http_user_agent)
        return isCookieClient

    def checkAccess(self):
        isAccessAllowed = False
        if self.app.debug:
            message = 'Checking access for: %s, %s, %s' % (
                self.authuserName,
                self.request.uri,
                self.request.method
            )
            self.loggerDebug(message)
        try:
            import kforge.apache.urlpermission as urlpermission
            isAccessAllowed = urlpermission.isAllowedAccess(
                self.authuserName,
                self.request.uri,
                self.request.method
            )
        except Exception, inst:
            if self.app.debug:
                message = 'Exception: %s' % str(inst)
                self.loggerDebug(message)
            raise
        if self.app.debug:
            if isAccessAllowed:
                message = "    ...allowing access."
                self.loggerDebug(message)
            else:
                message = "    ...not allowing access."
                self.loggerDebug(message)
        self.isAccessAllowed = isAccessAllowed
        return isAccessAllowed

    def loggerDebug(self, message):
        message = "%s handler: %s" % (
            self.__class__.__name__, 
            message
        )   
        self.app.logger.debug(message)


class PythonAccessHandler(ModPythonHandler):

    def __init__(self, *args, **kwds):
        super(PythonAccessHandler, self).__init__(*args, **kwds)
        self.session = None

    def initAuthuserNameFromCookie(self):
        self.authuserName = None
        authCookieValue = self.getAuthCookieValue()
        if authCookieValue:
            if self.app.debug:
                self.loggerDebug('Cookie: %s' % authCookieValue)
            import dm.view.base
            view = dm.view.base.ControlledAccessView(None)
            view.setSessionFromCookieString(authCookieValue)
            if view.session:
                self.session = view.session
                self.authuserName = self.session.person.name
            else:
                self.authuserName = self.app.dictionary[VISITOR_NAME]
        else:
            if self.app.debug:
                self.loggerDebug('No session cookie in request.')
            self.authuserName = self.app.dictionary[VISITOR_NAME]
        self.request.user = self.authuserName

    def getAuthCookieValue(self):
        authCookieName = self.app.dictionary[AUTH_COOKIE_NAME]
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
        if self.app.debug:
            self.loggerDebug('Redirecting to %s.' % redirectUri)
        self.request.status = HTTP_MOVED_TEMPORARILY


class PythonAuthenHandler(ModPythonHandler):

    def initAuthuserNameFromBasicPrompt(self):
        pw = self.request.get_basic_auth_pw()
        if self.app.debug:
            self.loggerDebug('Running initAuthuserNameFromBasicPrompt. Current user is %s.' % self.request.user)
        import kforge.apache.urlpermission as urlpermission
        self.authuserName = urlpermission.getVisitorName(
            self.request.user,
            pw
        )
        self.request.user = self.authuserName


