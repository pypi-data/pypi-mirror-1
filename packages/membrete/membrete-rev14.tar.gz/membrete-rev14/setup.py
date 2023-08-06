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

from distutils.core import setup

setup(
    name='membrete',
    description='Contact form app for Django',
    version='rev14',
    url='http://gonzalodelgado.com.ar/codigo/membrete',
    author='Gonzalo Delgado',
    author_email='gonzalodel@gmail.com',
    packages=['membrete', 'membrete.conf'],
    package_data={'membrete': ['templates/membrete/*.html']},
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'],
)
