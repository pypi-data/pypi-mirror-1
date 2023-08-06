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

from django.utils import simplejson
from django.core.mail import send_mail
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseRedirect
from membrete.conf import settings
from membrete.models import Message
from membrete.forms import ContactForm

logger = logging.getLogger('views')


def contact(
    request,
    form_class=ContactForm,
    post_save_redirect=None,
    fail_silently=settings.FAIL_SILENTLY,
    use_xhr=False,
    template_name='membrete/default.html',
    extra_context={}):
    """
    Valida los datos del formulario de contacto, envía el mensaje por correo
    a los destinatarios y guarda el mensaje en la base de datos.
    """
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.send(fail_silently=fail_silently)
            if request.is_ajax():
                data = {'valid': True}
                return HttpResponse(simplejson.dumps(data),
                                    mimetype='application/json')
            return HttpResponseRedirect(post_save_redirect or \
                                        reverse('membrete_sent'))
        elif request.is_ajax():
            errors = dict()
            for key, value in form.errors.iteritems():
                htmlid = form.fields[key].widget.attrs.get('id') or \
                                                           form[key].auto_id
                # Algunos valores de forms.errors contienen referencias a
                # traducciones, que no pueden serializarse.
                # Usando force_unicode, obtenemos las cadenas de caracteres de
                # las traducciones.
                errors[htmlid] = [force_unicode(v) for v in value]
            data = {'valid': False, 'errors': errors}
            return HttpResponse(simplejson.dumps(data),
                                mimetype='application/json')
    else:
        form = form_class()
    context = {'form': form}
    user = request.user
    if user.is_authenticated():
        user_can_receive_msg = user.has_perm('membrete.can_receive_messages')
        # Si es un usuario que pueda recibir mensajes de contacto, los podrá
        # ver por web. Lo mismo para los usuarios del staff
        if user_can_receive_msg or user.is_staff:
            messages = Message.objects.all()
            context.update({'messages': messages})
    context.update(extra_context)
    return render_to_response(template_name, RequestContext(request, context))
