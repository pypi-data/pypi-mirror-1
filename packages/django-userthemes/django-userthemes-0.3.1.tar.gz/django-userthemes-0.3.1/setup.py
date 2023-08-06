#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='django-userthemes',
      version='0.3.1',
      description='Django user themes application',
      author='Eric Veiras Galisson',
      author_email='eric AT sietch DASH tabr DOT com',
      url='http://bitbucket.org/daks/django-userthemes/',
      download_url='http://bitbucket.org/daks/django-userthemes/get/0.3.1.zip',
      license='GNU General Public License v2',
      packages=['userthemes', 'userthemes.templatetags'],
      classifiers=[
           'Development Status :: 4 - Beta',
           'Environment :: Web Environment',
           'Intended Audience :: Developers',
           'License :: OSI Approved :: GNU General Public License (GPL)',
           'Programming Language :: Python',
           'Framework :: Django',
       ],
    )
