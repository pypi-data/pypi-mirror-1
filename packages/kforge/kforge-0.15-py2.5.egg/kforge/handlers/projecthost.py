from kforge.handlers.modpython import PythonAccessHandler
from kforge.handlers.modpython import PythonAuthenHandler
from kforge.handlers.apachecodes import *

class ProjectAccessHandler(PythonAccessHandler):
    """
    Responsible for responding to and access control based upon session
    cookies, and for redirecting to the KForge login page or deferring control
    to the authen handler if access is not allowed, for clients which do 
    support cookies (such as Mozilla, Lynx, etc.).
    
    Please Note: ModPython access handlers must return OK to statisfy
    Apache's 'Satisfy any' condition, after which no further handling
    will be triggered. Returning HTTP_OK does not have the same
    effect, and further handlers may triggered wrongly. To repeat, the
    'Satisy any' condition is looking for any handler that returns 0.

        return OK       #      OK == 0     handling stops
        #return HTTP_OK # HTTP_OK == 200   handling would continue

    Redirect from an Authen Handler
    -------------------------------

    Overall there seems no easy way to achieve a redirect from an authen
    handler -- as of 2007-01-30 there is an outstanding (i.e. unanswered) faq
    item on precisely this issue:

    http://www.modpython.org/FAQ/faqw.py?req=show&file=faq03.033.htp

    
    COMMENT: So, let's document that OK and HTTP_FORBIDDEN both 'Satisfy' the
    "Satisfy any|all" condition, and see if we can set some other handler to
    clean up by setting any redirect if needed?    --JohnBywater


    WARNING: the proposed method below is *incorrect* but has been left here
    for documentation purposes. If, as suggested below, OK is returned though
    access handling *will* terminate the overall modpython request *will
    continue*.  Thus, for example, if you are trying to prevent a post request
    by redirecting the user to a login or accessDenied page you will have the
    confusing result that the (a) the redirect does happen but (b) the post
    still succeeds. This is because returning OK results in the continutation
    of the main mod_python request with the redirect only happening once this
    is completed.
    
    [[-- INCORRECT LEFT FOR DOC PURPOSES ONLY --
    
    If a handler returns OK, so that no further handlers will be called,
    then the HTTP response code can be set by setting the 'status'
    attribute on the request object received by the handler.

        self.request.status = HTTP_FORBIDDEN
        return OK


    For example, to redirect and be the last handler in a 'Satisfy any'
    condition, set the Location in the error headers, set the status to
    code HTTP_MOVED_TEMPORARILY, and then return OK:

        self.request.err_headers_out.add('Location', redirectUri)
        self.request.status = HTTP_MOVED_TEMPORARILY
        return OK


    This can be used in an Apache AccessHandler to avoid the 'Basic' prompt:

        Satisfy any
        Require valid-user
        PythonAccessHandler myhandlers::accesshandler  # method to redirect
        PythonAuthenHandler myhandlers::authenhandler
        AuthType Basic
        AuthName "%s Restricted Area"

    When an HTTP request encounters this configuration, the AccessHandler
    is called, and it sets the redirect location. It then returns OK, and
    the AuthenHandler is not called. The AuthenHandler prompt does not show,
    and the client is redirected as a result of the HTTP_MOVED_TEMPORARILY
    request status value, and the Location header.

    This technique is used in the authorise() method on this class.
    --]]
    """

    def authorise(self):
        self.initHandler()
        if not self.validateRequestUri():
            return HTTP_FORBIDDEN
        if self.isCookieClient(): 
            self.initAuthuserNameFromCookie()
            if self.checkAccess():
                return OK
            else:
                self.setLoginRedirect()
                # return HTTP_UNAUTHORIZED
                return HTTP_FORBIDDEN   # See above.
        else:
            self.initAuthuserNameFromDictionary()
            if self.checkAccess():
                return OK
            else:
                return HTTP_UNAUTHORIZED


class ProjectAuthenHandler(PythonAuthenHandler):
    """
    Responsible for authentication of and access control based upon
    credentials supplied through the 'Basic' password prompt for clients
    which don't support cookies (such as DAV, SVN, etc.).
    
    """
    
    def authorise(self):
        self.initHandler()
        if not self.validateRequestUri():
            return HTTP_FORBIDDEN
        if self.isCookieClient():
            self.loggerDebug("Cookie clients shouldn't get here.")
            return HTTP_FORBIDDEN
        self.initAuthuserNameFromBasicPrompt()
        if self.checkAccess():
            return OK
        else:
            return HTTP_UNAUTHORIZED


def accesshandler(request):
    handler = ProjectAccessHandler(request)
    return handler.authorise()
        
def authenhandler(request):
    handler = ProjectAuthenHandler(request)
    return handler.authorise()
 
