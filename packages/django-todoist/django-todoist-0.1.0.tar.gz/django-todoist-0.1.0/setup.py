#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2009 Andy Mikhailenko and contributors
#
#  This file is part of django-todoist.
#
#  django-todoist is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

from setuptools import setup
from todoist import __version__

setup(
    name     = 'django-todoist',
    version  = __version__,
    packages = ['todoist'],

    requires = ['python (>= 2.4)', 'django (>= 1.0)', 'httplib2 (>= 0.5)'],

    description  = 'Provides basic connectivity between Django and Todoist.',
    author       = 'Andy Mikhailenko',
    author_email = 'andy@neithere.net',
    url          = 'http://bitbucket.org/neithere/django-todoist/',
    download_url = 'http://bitbucket.org/neithere/django-todoist/get/tip.zip',
    license      = 'GNU Lesser General Public License (LGPL), Version 3',
    keywords     = 'django todoist sync',
    classifiers  = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
