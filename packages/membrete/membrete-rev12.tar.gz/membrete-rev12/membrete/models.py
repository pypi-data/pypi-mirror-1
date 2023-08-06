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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA

import logging
from datetime import datetime
from django.db import models, connection
from django.template import Context, Template
from django.core.mail import send_mail
from django.contrib.auth.models import User
from membrete.conf import settings
from membrete.managers import MessageTemplateManager

logger = logging.getLogger('models')

# Se podría extraer esto a una aplicación que contenga un tipo `Template',
# o bien tipo de campos (Field) `TemplateField'.
class MessageTemplate(models.Model):
    """
    Plantilla para enviar un mensaje.
    Se compone de un template para el asunto (`subject_template')
    y otro para el contenido (`content_template').
    Ambos se definen con la sintaxis de templates de Django.
    `content_template' recibe un contexto con los valores `datetime', `name',
    `mail', `phone', `website' y `message'.
    `subject_template' solo recibe el valor `subject' desde su contexto.
    """
    name = models.CharField('nombre', max_length=40)
    subject_template = models.TextField('plantilla de asunto')
    content_template = models.TextField('plantilla de contenido')
    default = models.BooleanField('plantilla por defecto')
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
        verbose_name = 'plantilla de mensaje'
        verbose_name_plural = 'plantillas de mensajes'


class Message(models.Model):
    """
    Un mensaje recibido a traves del formulario de contacto.
    El campo `sent' indica si el correo se envió o no.
    """
    name = models.CharField(u'nombre', max_length=80)
    company = models.CharField(u'empresa', max_length=80)
    mail = models.EmailField(u'email')
    phone = models.CharField(u'teléfono', max_length=30, blank=True)
    website = models.URLField(u'sitio web', blank=True, verify_exists=False)
    datetime = models.DateTimeField(u'fecha y hora', auto_now=True)
    subject = models.CharField('asunto', max_length=256, blank=True)
    message = models.TextField('mensaje')
    sent = models.BooleanField(u'enviado', default=False)
    template = models.ForeignKey(
        MessageTemplate,
        default=MessageTemplate.objects.get_default,
        verbose_name='plantilla')

    def __unicode__(self):
        return u'Mensaje de %s (%s)'%(self.name, self.mail)

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
        m = u"""
            El mensaje de contacto se enviará desde la dirección %s
            """ % from_email
        logger.debug(m)
        # Buscamos los usuarios que pueden recibir los mensajes
        recipient_list = [u.email for u in User.objects.all()
                                if u.has_perm('membrete.can_receive_message')
                                and u.email != '']
        recipient_list += extra_recipients
        # Sacamos las cadenas vacías de la lista
        while '' in recipient_list:
            logger.debug(u'Quitando cadena vacía')
            recipient_list.remove('')
        if len(recipient_list) == 0:
            self.sent = False
            m = u"""
                No se encontraron destinatarios para enviar el mensaje.
                Lista de destinatarios: %s
                """ % recipient_list
            logger.debug(m)
            if not fail_silently:
                self.save()
                raise ValueError('No recipients found')
        else:
            m = u"""Intentando enviar el siguiente mensaje:
                Asunto:\t%s
                Mensaje:\t%s
                Remitente:\t%s
                Destinatarios:\t%s""" % (
                    subject, message, from_email, recipient_list)
            logger.debug(m)
            # Enviamos el mensaje del formulario de contacto por mail a los
            # destinatarios.
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently)
            logger.debug(u'El mensaje se envió correctamente')
            self.sent = True
        self.save()

    class Meta:
        verbose_name = 'mensaje de contacto'
        verbose_name_plural = 'mensajes de contacto'
        permissions = (('can_receive_messages', 'Puede recibir mensajes'),)
