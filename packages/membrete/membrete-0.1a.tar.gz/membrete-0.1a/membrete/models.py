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

import logging
from datetime import datetime
from django.core.mail import send_mail
from django.db import models, connection
from django.contrib.auth.models import User
from django.template import Context, Template
from django.utils.translation import ugettext as _
from membrete.conf import settings
from membrete.managers import MessageTemplateManager

logger = logging.getLogger('models')

# Se podría extraer esto a una aplicación que contenga un tipo
# `Template', o bien tipo de campos (Field) `TemplateField'.
class MessageTemplate(models.Model):
    """
    Plantilla para enviar un mensaje.
    Se compone de un template para el asunto (`subject_template')
    y otro para el contenido (`content_template').
    Ambos se definen con la sintaxis de templates de Django.
    `content_template' recibe un contexto con los valores `datetime',
    `name', `mail', `phone', `website' y `message'.
    `subject_template' solo recibe el valor `subject' desde su contexto.
    """
    name = models.CharField(_(u'name'), max_length=40)
    subject_template = models.TextField(_('subject template'))
    content_template = models.TextField(_('content template'))
    default = models.BooleanField(_('is default'))
    objects = MessageTemplateManager()

    def render_content(self, context):
        if isinstance(context, dict):
            context = Context(context)
        return Template(self.content_template).render(context)

    def render_subject(self, context):
        if isinstance(context, dict):
            context = Context(context)
        return Template(self.subject_template).render(context)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if MessageTemplate.objects.count() == 0:
            self.default = True
        elif self.default and MessageTemplate.objects.exists_default():
            old_default = MessageTemplate.objects.get_default()
            old_default.default = False
            old_default.save()
        super(MessageTemplate, self).save(**kwargs)

    class Meta:
        verbose_name = _('message template')
        verbose_name_plural = _('message templates')


class Message(models.Model):
    """
    Un mensaje recibido a traves del formulario de contacto.
    El campo `sent' indica si el correo se envió o no.
    """
    name = models.CharField(_('name'), max_length=80)
    company = models.CharField(_('company'), max_length=80)
    mail = models.EmailField(_('email'))
    phone = models.CharField(_('phone'), max_length=30, blank=True)
    website = models.URLField(_('website'), blank=True, verify_exists=False)
    datetime = models.DateTimeField(_('date and time'), auto_now=True)
    subject = models.CharField(_('subject'), max_length=256, blank=True)
    message = models.TextField(_('message'))
    sent = models.BooleanField(_('is sent'), default=False)
    template = models.ForeignKey(MessageTemplate,
                                default=MessageTemplate.objects.get_default,
                                verbose_name=_('template'))

    def __unicode__(self):
        fromdata = {'name': self.name, 'mail': self.mail}
        return _('message from %(name)s (%(mail)s)') % fromdata

    def get_subject(self):
        context = Context({'subject': self.subject})
        return self.template.render_subject(context)

    def get_message(self):
        context = Context({
            'name': self.name,
            'mail': self.mail,
            'datetime': self.datetime,
            'website': self.website,
            'phone': self.phone,
            'message': self.message,
        })
        return self.template.render_content(context)

    def send(self, fail_silently=False, extra_recipients=[]):
        """
        Intenta enviar el mensaje por correo a los usuarios con permisos
        para recibir mensajes de contacto y a los indicados en la lista
        `extra_recipients'.
        El mensaje se envía mediante la plantilla `template'.
        En caso de fallar el envío del mail, se lanza una
        smtplib.SMTPException a menos que `fail_silently' sea False.
        En todos los casos, el mensaje es guardado en la base de datos.
        """
        if not self.datetime:
            self.datetime = datetime.now()
        subject = self.get_subject()
        message = self.get_message()
        from_email = settings.FROM_EMAIL
        m = _('contact message will be sent from %(from_email)s') % {
                                                    'from_email': from_email}
        logger.debug(m)
        # Buscamos los usuarios que pueden recibir los mensajes
        recipient_list = [u.email for u in User.objects.all()
                                if u.has_perm('membrete.can_receive_message')
                                and u.email != '']
        recipient_list += extra_recipients
        # Sacamos las cadenas vacías de la lista
        while '' in recipient_list:
            logger.debug(_('removing empty string'))
            recipient_list.remove('')
        if len(recipient_list) == 0:
            self.sent = False
            m = _('could not find any recipients')
            logger.debug(m)
            if not fail_silently:
                self.save()
                raise ValueError(m)
        else:
            m = _('attempting to send "%(subject)s" to %(recipients)s' % {
                            'subject': subject, 'recipients': recipient_list})
            logger.debug(m)
            # Enviamos el mensaje del formulario de contacto por mail a los
            # destinatarios.
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently)
            logger.debug(_('message sent'))
            self.sent = True
        self.save()

    class Meta:
        verbose_name = _('contact message')
        verbose_name_plural = _('contact messages')
        permissions = (('can_receive_messages', _('can receive messages')),)
