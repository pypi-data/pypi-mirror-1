from django.conf.urls.defaults import *
from kforge.soleInstance import application
uri_prefix = application.dictionary['www.uri_prefix']
if uri_prefix:
    uri_prefix = uri_prefix.lstrip('/')
    uri_prefix += '/'

urlpatterns = patterns('',
    (
        r'^%s' % uri_prefix, include('kforge.django.settings.urls.kui')
    ),
)

