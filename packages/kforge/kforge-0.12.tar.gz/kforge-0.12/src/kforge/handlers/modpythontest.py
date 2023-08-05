import unittest
from kforge.testunit import TestCase
from kforge.handlers.base import ModPythonHandler
from django.http import HttpRequest
from kforge.handlers.apachecodes import *

import os

def suite():
    suites = [
        unittest.makeSuite(TestModPythonHandler),
    ]
    return unittest.TestSuite(suites)


class ModPythonHandlerTestCase(TestCase):

    def setUp(self):
        self.makeHandler()

    def tearDown(self):
        self.request = None
        self.handler = None

    def makeRequest(self):
        self.request = self.requestClass()

    def makeHandler(self):
        self.makeRequest()
        self.handler = self.handlerClass(self.request)

    def test_handler(self):
        self.failUnless(self.handler)


class MockTableRecord(dict):

    def add(self, key, value):
        self[key] = value


class MockModPythonRequest(HttpRequest):

    def __init__(self):
        self.uri = '/warandpeace/example'
        self.method = 'GET'
        self.headers_in = MockTableRecord()
        self.headers_out = MockTableRecord()
        self.err_headers_out = MockTableRecord()
        self.subprocess_env = MockTableRecord()
        self.options = {
            'KFORGE_SETTINGS'       : os.environ['KFORGE_SETTINGS'],
            'DJANGO_SETTINGS_MODULE': os.environ['DJANGO_SETTINGS_MODULE'],
        }

    def get_options(self):
        return self.options

    def add_common_vars(self):
        pass


class TestModPythonHandler(ModPythonHandlerTestCase):

    handlerClass = ModPythonHandler
    requestClass = MockModPythonRequest

    def test_normalizeUriPath(self):
        self.handler.authorise()
        self.failUnlessEqual(
            self.handler.normalizeUriPath('/path/'),
            '/path',
        )

    def test_validateUri(self):
        self.handler.authorise()
        self.failUnless(self.handler.validateUri('/path/to/something/'))
        self.failUnless(self.handler.validateUri('/path'))
        self.failIf(self.handler.validateUri('/'))

    def test_authorise(self):
        self.failUnlessEqual(
            self.handler.authorise(),
            HTTP_UNAUTHORIZED
        )

