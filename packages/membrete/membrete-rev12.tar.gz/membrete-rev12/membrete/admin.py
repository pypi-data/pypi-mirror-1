# -*- coding: utf-8 -*-

# Copyright © 2008 Gonzalo Delgado
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

from django.contrib import admin
from membrete.models import Message, MessageTemplate

class MessageAdmin(admin.ModelAdmin):
    fieldsets = (
                 (None, {
                         'fields': ('name',
                                    'mail',
                                    'phone',
                                    'website',
                                    'subject',
                                    'message')}),
                 ('Avanzado', {
                               'classes': 'collapse',
                               'fields': ('template', )}))
    list_display = ('name', 'mail', 'datetime', 'sent')
    search_fields = ('name', 'mail')

admin.site.register(Message, MessageAdmin)

class MessageTemplateAdmin(admin.ModelAdmin):
    pass

admin.site.register(MessageTemplate, MessageTemplateAdmin)
