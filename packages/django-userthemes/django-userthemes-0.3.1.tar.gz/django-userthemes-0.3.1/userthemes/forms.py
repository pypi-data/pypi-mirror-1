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
from django.forms import ModelForm
from userthemes.models import UserTheme
from userthemes.config import themes_choices
from userthemes.middleware import get_current_theme


class UserThemeForm(ModelForm):
    """
    Form auto-generated from model UserTheme, excluding the user field.
    Choices are dynamically generated at load time.
    """
    def __init__(self, *args, **kwargs):
        super(UserThemeForm, self).__init__(*args, **kwargs)
        self.fields['theme'].choices = themes_choices()
        self.fields['theme'].initial = get_current_theme()

    class Meta:
        model = UserTheme
        exclude = ('user')

