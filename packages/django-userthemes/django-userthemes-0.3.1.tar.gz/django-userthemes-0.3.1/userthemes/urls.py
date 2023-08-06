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
Urls settings for django-userthemes
"""
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list, object_detail

from userthemes.views import edit_usertheme, create_usertheme


urlpatterns = patterns('',
    (r'^edit/$', login_required(edit_usertheme), {}, 'userthemes-edit'),
    (r'^create/$', login_required(create_usertheme), {}, 'userthemes-create'),
)

