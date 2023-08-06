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


from django import forms
from membrete.models import Message
from membrete.conf import settings


class ContactForm(forms.Form):
    name = forms.CharField(label=u'Nombre', max_length=60)
    company = forms.CharField(label=u'Empresa', max_length=60, required=False)
    mail = forms.EmailField(label=u'Email')
    phone = forms.CharField(
        label=u'Número de teléfono',
        max_length=30,
        required=False)
    website = forms.URLField(label=u'Sitio web', required=False)
    subject = forms.CharField(label=u'Asunto', max_length=100, required=False)
    message = forms.CharField(label=u'Mensaje', widget=forms.Textarea)

    def get_context(self):
        pass

    def send(self, fail_silently=False):
        if self.is_valid():
            cm = Message(
                name=self.cleaned_data['name'],
                company=self.cleaned_data['company'],
                mail=self.cleaned_data['mail'],
                phone=self.cleaned_data['phone'],
                website=self.cleaned_data['website'],
                subject=self.cleaned_data['subject'],
                message=self.cleaned_data['message'],
            )
            cm.send(fail_silently=fail_silently)
        else:
            raise ValueError('Can\'t send a message if form is not valid')
