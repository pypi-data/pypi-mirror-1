import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.project import ProjectListView

def suite():
    suites = [
        unittest.makeSuite(TestProjectListView),
    ]
    return unittest.TestSuite(suites)


class TestProjectListView(ViewTestCase):

    viewClass = ProjectListView

    def getRequiredViewContext(self):
        return {
            'objectCount': self.registry.projects.count()
        }

