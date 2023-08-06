import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.person import PersonListView

def suite():
    suites = [
        unittest.makeSuite(TestPersonListView),
    ]
    return unittest.TestSuite(suites)


class TestPersonListView(ViewTestCase):

    viewClass = PersonListView

    def getRequiredViewContext(self):
        return {
            'objectCount': self.registry.persons.count()
        }

