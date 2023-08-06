import kforge.django.settings.main
from dm.view.base import SessionView
import kforge.url

class KforgeView(SessionView):

    majorNavigation = [
        {'title': 'Home',      'url': '/'},
        {'title': 'Your Page', 'url': '/person/home/'},
        {'title': 'People',    'url': '/person/'},
        {'title': 'Projects',  'url': '/project/'},
    ]

    def setContext(self, **kwds):
        super(KforgeView, self).setContext(**kwds)
        # set here rather than on KforgeView
        # if set on KforgeView get error
        # 'thread._local' object has no attribute 'mapper'
        url_scheme = kforge.url.UrlScheme()
        self.context.update({
            'kforgeProjectHost' : self.dictionary['domain_name'],
            'kforge_media_url' : url_scheme.url_for_qualified('media'),
        })  

