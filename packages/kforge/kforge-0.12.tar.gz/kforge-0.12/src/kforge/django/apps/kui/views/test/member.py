import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.member import MemberListView
from kforge.django.apps.kui.views.member import MemberCreateView
from kforge.django.apps.kui.views.member import MemberUpdateView
from kforge.django.apps.kui.views.member import MemberDeleteView

def suite():
    suites = [
        unittest.makeSuite(TestMemberListView),
        unittest.makeSuite(TestMemberCreateView),
        unittest.makeSuite(TestMemberUpdateView),
        unittest.makeSuite(TestMemberDeleteView),
    ]
    return unittest.TestSuite(suites)


class MemberViewTestCase(ViewTestCase):

    projectName = 'administration'
    requiredRedirect = '/login/'
    requiredResponseClassName = 'HttpResponseRedirect'

    def createViewKwds(self):
        viewKwds = super(MemberViewTestCase, self).createViewKwds()
        viewKwds['domainObjectKey'] = self.projectName
        return viewKwds
    
    def test_canAccess(self):
        self.failIf(self.view.canAccess())


class TestMemberListView(MemberViewTestCase):

    viewClass = MemberListView
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponse'

    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberCreateView(MemberViewTestCase):

    viewClass = MemberCreateView
        

class TestMemberUpdateView(MemberViewTestCase):

    viewClass = MemberUpdateView
    

class TestMemberDeleteView(MemberViewTestCase):

    viewClass = MemberDeleteView
 
