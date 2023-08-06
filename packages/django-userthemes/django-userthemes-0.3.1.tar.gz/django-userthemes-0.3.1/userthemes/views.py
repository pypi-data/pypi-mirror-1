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
    Views for creating and editing user theme preference. 
"""
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from userthemes.models import UserTheme
from userthemes.forms import UserThemeForm
from userthemes.middleware import get_current_user


def create_usertheme(request,
                     form_class=None,
                     template_name='userthemes/create_usertheme.html',
                     success_url=None):
    """
    Create a user theme for the current user, if one doesn't already
    exist.
    
    If the user already has a UserTheme, a redirect will be issued to the
    :view:`userthemes.views.edit_usertheme` view.
    
    Optional arguments
    * form_class
    * template_name
    * success_url
    """
    user_id = get_current_user().id
    
    if success_url is None:
        success_url = reverse('userthemes-edit')
        
    try:
        usertheme_obj = UserTheme.objects.get(user=user_id)
        return HttpResponseRedirect(reverse('userthemes-edit'))
    except ObjectDoesNotExist:
        pass
    
    if form_class is None:
        form_class = UserThemeForm
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            usertheme_obj = form.save(commit=False)
            usertheme_obj.user_id = user_id
            usertheme_obj.save()
            response = HttpResponseRedirect(success_url)
            response.set_cookie("usertheme", form.cleaned_data['theme'])
            return response
    else:
        form = form_class()
    
    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request))


def edit_usertheme(request,
                   form_class=None,
                   template_name='userthemes/edit_usertheme.html',
                   success_url=None):
    """
    Edit the current user's theme.
    
    If the user does not already have a UserTheme, a redirect will be issued
    to the :view:`userthemes.views.create_usertheme` view.
    
    Optional arguments
    * form_class
    * template_name
    * success_url
    """
    user_id = get_current_user().id

    if success_url is None:
        success_url = reverse('userthemes-edit')
    
    try:
        usertheme_obj = UserTheme.objects.get(user=user_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('userthemes-create'))
      
    if form_class is None:
        form_class = UserThemeForm
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=usertheme_obj)
        if form.is_valid():
            usertheme_obj = form.save(commit=False)
            usertheme_obj.user_id = user_id
            usertheme_obj.save()
            response = HttpResponseRedirect(success_url)
            response.set_cookie("usertheme", form.cleaned_data['theme'])
            return response
    else:
        form = form_class()
    
    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request))

