# -*- coding: utf-8 -*-

from os import path as ospath
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

# Pasamos `document_root' por `unicode' para permitir nombres de archivo y/o
# directorios con caracteres que no sean ascii
media_dict = {'document_root': settings.MEDIA_ROOT}

urlpatterns = patterns('',
    (r'', include('membrete.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', media_dict),
)
