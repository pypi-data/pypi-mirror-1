from webunit import webunittest
import unittest
import os
from StringIO import StringIO

import twill
from twill import commands as web

os.environ['DJANGO_SETTINGS_MODULE'] = 'kforge.django.settings.main'

import django.core.handlers.wsgi

import kforge.soleInstance
import kforge.url
import random


class KuiTestCase(webunittest.WebTestCase):

    system = kforge.soleInstance.application
    registry = kforge.soleInstance.application.registry
    kuiServer = kforge.url.UrlScheme().getFqdn()
    # use a random port now that we are inserting an intercept
    # kuiPort = system.dictionary['www.port_http']
    kuiPort = 8080
    ok_code = 200
    url_scheme = kforge.url.UrlScheme()

    def createNumber(self):
        return str(random.randint(1, 10000000))

    def setUp(self):
        wsgi_app = django.core.handlers.wsgi.WSGIHandler()
        twill.add_wsgi_intercept(self.kuiServer, self.kuiPort, lambda : wsgi_app)
        # while we're at it, stop twill from running off at the mouth...
        self.outp = StringIO()
        # comment this out if you want verbose output ...
        twill.set_output(self.outp)

        self.siteurl = 'http://%s:%s' % (self.kuiServer, self.kuiPort)

        self.setServer(self.kuiServer, self.kuiPort)
        self.kuiPersonName = 'kuitest' + self.createNumber()
        self.kuiPersonPassword = 'kuitest'
        self.kuiPersonEmail    = 'kuitest@appropriatesoftware.net'
        self.kuiPersonFullname = 'kuitestfullname'
        self.kuiProjectFullname = 'kuitestfullname'
        self.kuiProjectName = 'kuitest' + self.createNumber()
        self.kuiProjectDescription = 'kuitest project description'
        self.kuiProjectLicense = '1'
   
    def tearDown(self):
        twill.remove_wsgi_intercept('localhost', 8080)

    def getAssertContent(self, url, content, code=ok_code):
        fullurl = self.siteurl + url
        web.go(fullurl)
        web.code(code)
        self.webFind(content)

    def webFind(self, requirement):
        if type(requirement) == str:
            regexp = requirement
            web.find(regexp)
        elif type(requirement) == list:
            for regexp in requirement:
                web.find(regexp)
        else:
            raise Exception, "Requirement not <type 'str'> or <type 'list'>."

    def getAssertNotContent(self, url, content, code=ok_code):
        fullurl = self.siteurl + url
        web.go(fullurl)
        web.code(code)
        web.notfind(content)

    def post(self, url, params, code=ok_code):
        fullurl = self.siteurl + url
        web.go(fullurl)
        web.code(200)
        # since we always have login form at top of each page form number is 2
        form_number = 2 
        for k,v in params.items():
            web.fv(form_number, k, v)
        # sometimes params is empty so need to set form explicitly
        # e.g. for deletes
        if len(params) == 0:
            # hit a field, any field ...
            web.fv(2, 1, '')
        web.submit()
        web.code(code)

    def postAssertContent(self, url, params, content, code=ok_code):
        self.post(url, params)
        web.find(content)

    def postAssertNotContent(self, url, params, content, code=ok_code):
        self.post(url, params)
        web.notfind(content)

    def _check_home(self):
        offset = self.url_scheme.url_for('home')
        url = self.siteurl + offset
        web.go(url)
        web.code(200)

    def registerPerson(self):
        params = {}
        params['name'] = self.kuiPersonName
        params['password'] = self.kuiPersonPassword
        params['passwordconfirmation'] = self.kuiPersonPassword
        params['fullname'] = self.kuiPersonFullname
        params['email'] = self.kuiPersonEmail
        params['emailconfirmation'] = self.kuiPersonEmail
        offset = self.url_scheme.url_for('person', action='create')
        self.post(offset, params)
        offset = self.url_scheme.url_for('person', action='read',
                id=self.kuiPersonName)
        self.getAssertContent(offset, self.kuiPersonName)

    def _login(self, username, password):
        offset = self.url_scheme.url_for('login')
        url = self.siteurl + offset
        web.go(url)
        web.code(200)
        web.find('KForge - Log in') # page title
        formname = 2 # use index as name ('') does not seem to work
        web.fv(formname, 'name', username)
        web.fv(formname, 'password', password)
        web.submit()
        web.code(200)
        web.notfind('Sorry, wrong user name or password.')
        web.find('Logged in')
        web.find('You are now logged in as')
    
    def _logout(self):
        offset = self.url_scheme.url_for('logout')
        url = self.siteurl + offset
        web.go(url)
        web.code(200)
        web.find('You&rsquo;ve successfully logged out of KForge.')

    def loginPerson(self):
        self._login(self.kuiPersonName, self.kuiPersonPassword) 

    def deletePerson(self):
        params = {}
        offset = self.url_scheme.url_for('person', action='delete',
                id=self.kuiPersonName)
        self.post(offset, params)

    def registerProject(self):
        params = {}
        params['name'] = self.kuiProjectName
        params['title'] = self.kuiProjectFullname
        params['licenses'] = self.kuiProjectLicense
        params['description'] = self.kuiProjectDescription
        offset = self.url_scheme.url_for('project', action='create')
        self.post(offset, params)
        requiredContent = self.kuiProjectName
        offset = self.url_scheme.url_for('project')
        self.getAssertContent(offset, requiredContent)
        offset = self.url_scheme.url_for('project', action='read',
                id=self.kuiProjectName)
        self.getAssertContent(offset, requiredContent)

    def deleteProject(self):
        offset = self.url_scheme.url_for('project', action='delete',
                id=self.kuiProjectName)
        params = {}
        self.post(offset, params)
        while self.kuiProjectName in self.system.registry.projects:
            project = self.system.registry.projects[self.kuiProjectName]
            project.delete()
            project.purge()
        requiredContent = self.kuiProjectName
        offset = self.url_scheme.url_for('project')
        self.getAssertNotContent(offset, requiredContent)

