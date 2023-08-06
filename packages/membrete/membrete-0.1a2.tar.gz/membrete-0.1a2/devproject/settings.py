# -*- coding: utf-8 -*-

# Copyright © 2009 Gonzalo Delgado
#
# This file is part of membrete.
#
# membrete is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3 of
# the License, or (at your option) any later version.
#
# membrete is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with membrete. If not, see
# <http://www.gnu.org/licenses/>.

# Django settings for membrete sample project.

import os

PROJECT_DIR = unicode(os.path.abspath(os.path.dirname(__file__)), 'utf-8')

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'membrete.db'
USE_I18N = True
MEDIA_ROOT = os.path.realpath(os.path.join(PROJECT_DIR, u'../membrete/media'))
MEDIA_URL = '/site_media/'
ADMIN_MEDIA_PREFIX = '/media/'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
)
ROOT_URLCONF = 'urls'
TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, u'templates'),
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'membrete',
)
# Try to load and override default project settings from private_settings.py
# such as database or email configuration.
# You can define site specific private settings such as SECRET_KEY, EMAIL_HOST,
# MANAGERS, etc. in a file named private_settings.py.
try:
    from private_settings import *
except ImportError:
    pass
