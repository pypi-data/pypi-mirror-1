from django.conf.urls.defaults import *
from desire.soleInstance import application
from desire.dictionarywords import URI_PREFIX

uriPrefix = application.dictionary[URI_PREFIX]

if uriPrefix:
    uriPrefix = uriPrefix.lstrip('/')
    uriPrefix = uriPrefix + '/'

urlpatterns = patterns('',
    (
        r'^%s' % uriPrefix, include('desire.django.settings.urls.eui')
    ),
)

