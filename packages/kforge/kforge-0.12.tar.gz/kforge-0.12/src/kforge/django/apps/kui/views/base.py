import kforge.django.settings.main
from dm.view.base import SessionView

class KforgeView(SessionView):

    majorNavigation = [
        {'title': 'Home',      'url': '/'},
        {'title': 'Your Page', 'url': '/person/home/'},
        {'title': 'People',    'url': '/person/'},
        {'title': 'Projects',  'url': '/project/'},
    ]

    def setContext(self, **kwds):
        super(KforgeView, self).setContext(**kwds)
        self.context.update({
            'kforgeProjectHost' : 'project.' + self.dictionary['domain_name'],
        })  

