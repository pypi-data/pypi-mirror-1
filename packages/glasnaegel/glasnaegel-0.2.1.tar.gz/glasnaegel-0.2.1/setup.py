#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2010 Andrey Mikhaylenko and contributors
#
#  This file is part of Glasnägel.
#
#  Glasnägel is free software under terms of the GNU Lesser General Public
#  License version 3 (LGPLv3) as published by the Free Software Foundation.
#  See the file README for copying conditions.
#

import os
from setuptools import setup
import glasnaegel


readme = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(
    name     = 'glasnaegel',
    version  = glasnaegel.__version__,
    packages = ['glasnaegel'],

    requires = ['python (>= 2.4)', 'glashammer (>= 0.3.0)'],

    description  = 'A set of shortcuts for the Glashammer web framework.',
    long_description = readme,
    author       = 'Andrey Mikhaylenko',
    author_email = 'andy@neithere.net',
    url          = 'http://bitbucket.org/neithere/glasnaegel/',
    download_url = 'http://bitbucket.org/neithere/glasnaegel/get/tip.zip',
    license      = 'GNU Lesser General Public License (LGPL), Version 3',
    keywords     = 'Glashammer',
    classifiers  = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        #'Framework :: Glashammer',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
