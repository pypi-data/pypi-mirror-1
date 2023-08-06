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
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.utils._os import safe_join

from userthemes.middleware import get_current_theme
from userthemes.config import THEMES_DIR, DEFAULT_THEME


def load_template_source(template_name, template_dirs=None):
    """
    Loads the ``template_name`` supplied, by searching in the ``THEMES_DIR``.
    It first searches for the file in the current user theme preference and if
    it can't find it, searches in the default theme preference.
    """
    tried = []
    if not template_dirs:
        template_dirs = settings.TEMPLATE_DIRS
    
    for template_dir in template_dirs:
        try:
            
            try:
                # first try to find template in the specified theme directory
                filepath = safe_join(template_dir, THEMES_DIR, get_current_theme(), template_name)
            except UnicodeDecodeError:
                # The template dir name was a bytestring that wasn't valid UTF-8.
                raise
            except ValueError:
                # The joined path was located outside of this particular
                # template_dir (it might be inside another one, so this isn't
                # fatal).
                pass
            else:
                return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
        
        except IOError:
            try:
                
                try:
                    # if the template is not found, search in the default theme directory
                    filepath = safe_join(template_dir, THEMES_DIR, DEFAULT_THEME, template_name)
                except UnicodeDecodeError:
                    raise
                except ValueError:
                    pass                
                else:
                    return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
                pass
            
            except IOError:
                tried.append(filepath)
        
    if tried:
        error_msg = "Tried %s" % tried
    else:
        error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
    raise TemplateDoesNotExist, error_msg

load_template_source.is_usable = True

