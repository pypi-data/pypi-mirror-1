#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Éric Veiras Galisson.
# 
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#
"""
Configuration module for the django_userthemes application.

It retrieves the following settings from the project settings, or set it if 
necessary. See ``docs/configuration.txt`` for information on how to change it.

* THEMES_DIR indicates in which subdirectory themes will be searched for.
It defaults to 'themes'
* DEFAULT_THEME is the name of the default theme used. Initialized at 'default'
* TEMPLATES_DIR is where application will search for THEMES_DIR, by default 
it's TEMPLATES_DIR[0]
* STATIC_URL is the url path for static content that webserver uses
(http://my.domain.tld/static -> /static)

It also generates
* THEMES_CHOICE with is a tuple of tuples equals to theme names
"""
from django.conf import settings
from django.utils.translation import ugettext as _
import os

#
THEMES_DIR = getattr(settings, 'DJUT_THEMES_DIR', 'themes')
    
#
DEFAULT_THEME = getattr(settings, 'DJUT_DEFAULT_THEME', 'default')

#
TEMPLATES_DIR = getattr(settings, 'DJUT_TEMPLATES_DIR', settings.TEMPLATE_DIRS[0])

#
def themes_choices():
    TMP_THEMES_CHOICE = ((DEFAULT_THEME, _('default theme')),)
    for theme in os.listdir(os.path.join(TEMPLATES_DIR, THEMES_DIR)):
        if theme == DEFAULT_THEME:
            x = (theme, theme + _(' (default)'))
        else:
            x = (theme, theme)
        TMP_THEMES_CHOICE += (x,)
    return TMP_THEMES_CHOICE

THEMES_CHOICE = themes_choices()

#
STATIC_URL = getattr(settings, 'DJUT_STATIC_URL', '/static')

