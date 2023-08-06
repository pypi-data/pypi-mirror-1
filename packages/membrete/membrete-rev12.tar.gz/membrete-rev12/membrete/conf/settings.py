# -*- coding: utf-8 -*-

# Copyright © 2008 Gonzalo Delgado
#
# This file is part of membrete.
#
# membrete is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# membrete is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with membrete; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301xx
# USA


from django.conf import settings
from django.contrib.sites.models import Site

DEBUG = getattr(settings, 'DEBUG', True)
MAIL_ADMINS = getattr(settings, 'MEMBRETE_MAIL_ADMINS', False)
MAIL_MANAGERS = getattr(settings, 'MEMBRETE_MAIL_MANAGERS', True)
USE_FORM_EMAIL = getattr(settings, 'MEMBRETE_USE_FORM_EMAIL', False)
FROM_EMAIL = getattr(
    settings,
    'MEMBRETE_FROM_EMAIL',
    settings.DEFAULT_FROM_EMAIL)
SENT_URL = getattr(settings, 'MEMBRETE_SENT_URL', 'enviado')
NOTIFY_SENT = getattr(settings, 'MEMBRETE_NOTIFY_SENT', True)
FAIL_SILENTLY = getattr(settings, 'MEMBRETE_FAIL_SILENTLY', True)
