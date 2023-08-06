#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2009 Andy Mikhailenko and contributors
#
#  This file is part of Django Harness.
#
#  Django Harness is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

" Django Harness setup "

from setuptools import setup, find_packages
import harness

setup(
    name         = 'django-harness',
    version      = harness.__version__,
    packages     = find_packages(exclude=['blank_site', 'example']),
    
#    install_requires = ['python >= 2.4', 'django >= 1.0'],
    
    description  = 'Settings on steroids for Django',
    long_description = 'Django Harness is an application for Django Web Framework providing typical default settings for a website.',
    author       = 'Andy Mikhailenko',
    author_email = 'andy@neithere.net',
    url          = 'http://bitbucket.org/neithere/django-harness/',
    download_url = 'http://bitbucket.org/neithere/django-harness/src/',
    license      = 'GNU Lesser General Public License (LGPL), Version 3',
    keywords     = 'django settings conf',
)
