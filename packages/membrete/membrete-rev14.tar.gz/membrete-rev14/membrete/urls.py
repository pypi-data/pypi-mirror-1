# -*- coding: utf-8 -*-

# Copyright © 2009 Gonzalo Delgado
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA


from os import path as ospath
from django.utils.translation import ugettext as _
from membrete.conf import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('membrete.views',
    url(regex=r'^/?$', view='contact', name='membrete_contact'),
)


print _('hello')
print _('good bye')

sent_url = settings.SENT_URL 

urlpatterns += patterns('django.views.generic.simple',
    url(regex=r'^%s/$' % sent_url,
        view='direct_to_template',
        kwargs={'template': 'membrete/sent.html'},
        name='membrete_sent'),
)

urlpatterns += patterns('django.views.i18n',
    url(regex='^jsi18n$',
        view='javascript_catalog',
        name='jsi18n',
        kwargs={'packages': 'membrete'}),
)
