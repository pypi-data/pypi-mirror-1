#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2004-2008 Konstantin Knizhnik
# All rights reserved

import sys
from glob import glob

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

from distutils import sysconfig

# NOTE: The following "hack" removes the -Wstrict-prototypes
# build option from the command that will compile the C++ module,
removals = ['-Wstrict-prototypes']

if sys.version_info >= (2, 5):
    optname = 'CFLAGS'
else:
    optname = 'OPT'

opts = sysconfig.get_config_vars().get(optname, None)
if opts:
    for removal in removals:
        opts = opts.replace(removal, ' ')
    sysconfig.get_config_vars()[optname] = ' '.join(opts.split())

setup(
    name = 'DyBASE',
    version = '0.20.0',
    description = 'An embedded OO database',
    long_description = \
"""DyBASE is very simple object oriented embedded database
for languages with dynamic type checking.""",
    author = 'Konstantin Knizhnik',
    author_email = 'knizhnik@garret.ru',
    license = 'MIT License',
    url = 'http://www.garret.ru/~knizhnik/dybase.html',
    zip_safe = True,

    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages = ['dybase'],

    ext_modules = [
        Extension(
            name = 'dybase._dybase',
            include_dirs = ['../inc'],
            libraries = [],
            extra_compile_args = [],
            sources = glob('../src/*.cpp') + glob('dybase/dybaseapi.c'),
        )
    ],
)
