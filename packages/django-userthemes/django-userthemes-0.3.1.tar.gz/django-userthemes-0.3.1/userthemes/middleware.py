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
    django-userthemes middleware

    This middleware does two things:
    * first, it provides a way to access information about the current user outside 
    requests. Comes from http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser
    * second, it sets an HTTP cookie for the usertheme preference in order to
    limit SQL queries
"""
from django.conf import settings
import django
from userthemes.config import DEFAULT_THEME
from userthemes.models import UserTheme

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
def get_current_user():
    """
    Returns the locally stored user variable
    """
    return getattr(_thread_locals, 'user', None)
      
def get_current_theme():
    """
    Returns the locally stored theme variable
    """
    return getattr(_thread_locals, 'theme', None)

class UserThemesMiddleware(object):
    """
    Middleware that gets various objects from the
    request object and saves them in thread local storage.
    It implements process_request and process_response to do so and to set
    an HTTP cookie to limit SQL queries
    """
    
    def __init__(self):
        """
        Initialise the middleware by setting the default theme to 
        config.DEFAULT_THEME
        """
        self.default_theme = DEFAULT_THEME
 
    def process_request(self, request):
        """
        Sets user and theme local variables to make it available in the middleware
        * user is found in the request supplied
        * theme is found in an HTTP cookie, in the database (UserTheme model)
        or uses the default one
        """
        _thread_locals.user = getattr(request, 'user', None)
        if request.COOKIES.has_key('usertheme'):
            _thread_locals.theme = request.COOKIES['usertheme']
        else:
            try:
                _thread_locals.theme = UserTheme.objects.get(user=_thread_locals.user.id).theme
            except UserTheme.DoesNotExist:
                _thread_locals.theme = self.default_theme
        
    def process_response(self, request, response):
        """
        Sets the theme local variable to make it available in the middleware, like
        the ``process_request`` below does.
        It also alters the HttpResponse object by adding an HTTP cookie called
        usertheme and sets to the used theme
        If no user is authenticated, the cookie is deleted.
        """
        if request.user.is_authenticated():
            if not request.COOKIES.has_key('usertheme'):
                theme = self.default_theme
                try:
                    theme = UserTheme.objects.get(user=request.user.id).theme
                except UserTheme.DoesNotExist:
                    pass
                _thread_locals.theme = theme
                response.set_cookie("usertheme", theme)            
        else:
            _thread_locals.theme = self.default_theme
            response.delete_cookie("usertheme")
        return response

