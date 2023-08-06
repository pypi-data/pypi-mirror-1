from django.conf.urls.defaults import *
from scanbooker.soleInstance import application
from scanbooker.dictionarywords import URI_PREFIX

uriPrefix = application.dictionary[URI_PREFIX]

if uriPrefix:
    uriPrefix = uriPrefix.lstrip('/')
    uriPrefix = uriPrefix + '/'

urlpatterns = patterns('',
    (
        r'^%s' % uriPrefix, include('scanbooker.django.settings.urls.sui')
    ),
)

