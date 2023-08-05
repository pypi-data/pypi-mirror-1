from kforge.django.apps.kui.views.base import KforgeView
import kforge.command

class WelcomeView(KforgeView):

    templatePath = 'index'
    minorNavigationItem = '/'

    def __init__(self, **kwds):
        super(WelcomeView, self).__init__(**kwds)

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/'},
        ]
        if self.session:
            self.minorNavigation.append(
                {'title': 'Log out',   'url': '/logout/'}
            )
            self.minorNavigation.append(
                {'title': 'Join project',       'url': '/project/'}
            )
        else:
            self.minorNavigation.append(
                {'title': 'Log in',      'url': '/login/'},
            )
            self.minorNavigation.append(
                {'title': 'Register',      'url': '/person/create/'},
            )

    def canAccess(self):
        return self.canReadSystem()

    def setContext(self, **kwds):
        super(WelcomeView, self).setContext(**kwds)
        projects = self.registry.projects
        projectCount = len(projects)
        persons = self.registry.persons
        personCount = len(persons)
        self.context.update({
            'projectCount' : projectCount,
            'personCount'  : personCount,
        })


class PageNotFoundView(WelcomeView):

    templatePath = 'pageNotFound'


class AccessControlView(KforgeView):

    templatePath = 'accessDenied'
    minorNavigationItem = ''

    def __init__(self, deniedPath='', **kwds):
        super(AccessControlView, self).__init__(**kwds)
        self.deniedPath = deniedPath

    def setMinorNavigationItems(self):
        self.minorNavigation = [
            {'title': 'Welcome', 'url': '/'},
        ]
        if self.session:
            self.minorNavigation.append(
                {'title': 'Log out',   'url': '/logout/'}
            )
            self.minorNavigation.append(
                {'title': 'Join project',       'url': '/project/'}
            )
        else:
            self.minorNavigation.append(
                {'title': 'Log in',      'url': '/login/'},
            )
            self.minorNavigation.append(
                {'title': 'Register',      'url': '/person/create/'},
            )
    
    def canAccess(self):
        return self.canReadSystem()
        
    def setContext(self, **kwds):
        super(AccessControlView, self).setContext(**kwds)
        self.context.update({
            'deniedPath'  : self.deniedPath,
        })


def welcome(request):
    view = WelcomeView(request=request)
    return view.getResponse()

def pageNotFound(request):
    view = PageNotFoundView(request=request)
    return view.getResponse()

def accessDenied(request, deniedPath):
    view = AccessControlView(request=request, deniedPath=deniedPath)
    return view.getResponse()


