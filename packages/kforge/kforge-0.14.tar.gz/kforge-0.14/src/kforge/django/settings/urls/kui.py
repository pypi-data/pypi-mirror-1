from django.conf.urls.defaults import *
import re
import kforge.re
# import kforge.url
# url_scheme = kforge.url.UrlScheme()

urlpatterns = patterns('kforge.django.apps.kui.views',

    #
    ##  Application Home Page

    (r'^$',
        'kui.welcome'),

    #
    ##  User Authentication

    (r'^login/(?P<returnPath>(.*))$',
        'accesscontrol.login'),
    (r'^logout(?P<redirect>(.+))$',
        'accesscontrol.logout'),

    #
    ##  Generic Application View 

#    (r'^admin/(?P<caseName>(\w*))/(?P<actionName>(\w*))/((?P<className>(\w*))/((?P<objectKey>([^/]*)))/)$',
#        'admin.view'),

    #
    ##  Administration
    
    (r'^admin/model/create/(?P<className>(\w*))/$',
        'admin.create'),

    (r'^admin/model/update/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.update'),

    (r'^admin/model/delete/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.delete'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.listHasMany'),

    (r'^admin/model/create/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.createHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.readHasMany'),

    (r'^admin/model/update/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.updateHasMany'),

    (r'^admin/model/delete/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.deleteHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/$',
        'admin.read'),

    (r'^admin/model/(?P<className>([^/]*))/$',
        'admin.list'),

    (r'^admin/model/$',
        'admin.model'),

    (r'^admin/$',
        'admin.index'),


    #
    ##  Access Control
    
    (r'^accessDenied/(?P<deniedPath>(.*))$',
        'kui.accessDenied'),

    #
    ##  Person

    (r'^person/create/(?P<returnPath>(.*))$',
        'person.create'),
        
    (r'^person/$',
        'person.list'),
        
    (r'^person/find/(?P<startsWith>[\w\d]+)/$',
        'person.search'),
        
    (r'^person/find/$',
        'person.search'),
        
    (r'^person/search/$',
        'person.search'),
        
    (r'^person/home/$',
        'person.read'),
        
    (r'^person/(?P<personName>%s)/$' % kforge.re.personName,
        'person.read'),
        
    (r'^person/(?P<personName>%s)/home/$' % kforge.re.personName,
        'person.read'),
        
    (r'^person/(?P<personName>%s)/edit/$' % kforge.re.personName,
        'person.update'),
        
    (r'^person/(?P<personName>%s)/delete/$' % kforge.re.personName,
        'person.delete'),

    #
    ##  Project

    (r'^project/create/(?P<returnPath>(.*))$',
        'project.create'),
        
    (r'^project/$',
        'project.list'),
        
    (r'^project/find/(?P<startsWith>[\w\d]+)/$',
        'project.search'),
        
    (r'^project/find/$',
        'project.search'),
        
    (r'^project/search/$',
        'project.search'),
        
    (r'^project/home/$',
        'project.read'),
        
    (r'^project/(?P<projectName>%s)/$' % kforge.re.projectName,
        'project.read'),
        
    (r'^project/(?P<projectName>%s)/home/$' % kforge.re.projectName,
        'project.read'),
        
    (r'^project/(?P<projectName>%s)/edit/$' % kforge.re.projectName,
        'project.update'),
        
    (r'^project/(?P<projectName>%s)/delete/$' % kforge.re.projectName,
        'project.delete'),
        

    #
    ##  Member

    (r'^project/(?P<projectName>%s)/members/$' % kforge.re.projectName,
        'member.list'),
        
    (r'^project/(?P<projectName>%s)/members/create/$' % kforge.re.projectName,
        'member.create'),
        
    (r'^project/(?P<projectName>%s)/members/(?P<personName>%s)/edit/$' % (
        kforge.re.projectName, kforge.re.personName),  
        'member.update'),
        
    (r'^project/(?P<projectName>%s)/members/(?P<personName>%s)/delete/$' % (
        kforge.re.projectName, kforge.re.personName),  
        'member.delete'),

    #
    ##  Service
    
    (r'^project/(?P<projectName>%s)/services/$' % kforge.re.projectName,
        'service.list'),

    (r'^project/(?P<projectName>%s)/services/create/$' % kforge.re.projectName,
        'service.create'),

    (r'^project/(?P<projectName>%s)/services/(?P<serviceName>%s)/edit/$' % (
        kforge.re.projectName, kforge.re.serviceName),  
        'service.update'),

    (r'^project/(?P<projectName>%s)/services/(?P<serviceName>%s)/delete/$' % (
        kforge.re.projectName, kforge.re.serviceName),  
        'service.delete'),

    (r'^project/(?P<projectName>%s)/services/(?P<serviceName>%s)/$' % (
        kforge.re.projectName, kforge.re.serviceName),  
        'service.read'),

    (r'^project/(?P<projectName>%s)/services/(?P<serviceName>%s)/extn/create/$' % (
        kforge.re.projectName, kforge.re.serviceName),
        'service.extnCreate'),

    (r'^project/(?P<projectName>%s)/services/(?P<serviceName>%s)/extn/update/$' % (
        kforge.re.projectName, kforge.re.serviceName),
        'service.extnUpdate'),

    #
    ##  Not Found

    (r'^.*$',
        'kui.pageNotFound'),
)

