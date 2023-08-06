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

import logging
from django.db import models, connection
from django.utils.translation import ugettext as _


class MessageTemplateManager(models.Manager):
    DEFAULT_TEMPLATE_DICT = {'name': u'default',
                             'subject_template': u'{{ subject }}',
                             'content_template': '\n'.join([
                                        _('date and time') + ':\t{{datetime}}',
                                        _('name') + ':\t{{name}}',
                                        _('phone') + ':\t{{phone}}',
                                        _('mail') + ':\t{{website}}',
                                        _('message') + ':\n{{message}}']),
                             'default': True}

    def exists_default(self):
        qs = len(super(MessageTemplateManager, self).filter(default=True))
        return qs > 0

    def get_default(self):
        """
        Devuelve la plantilla por defecto (campo `default' True).
        Si no existiera crea una con los valores de DEFAULT_TEMPLATE_DICT
        """
        superclass = super(MessageTemplateManager, self)
        mesg_template, created = superclass.get_or_create(default=True)
        temp_dict = MessageTemplateManager.DEFAULT_TEMPLATE_DICT
        if created:
            mesg_template.name = temp_dict['name']
            mesg_template.subject_template = temp_dict['subject_template']
            mesg_template.content_template = temp_dict['content_template']
            mesg_template.save()
            msg = _('default template created: %(template_name)s')
            logging.debug(msg % {'template_name': mesg_template})
        return mesg_template
