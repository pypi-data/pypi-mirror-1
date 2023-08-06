#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import os

from setuptools import setup

setup(
    name = 'TracShellExampleMacro',
    version = '1.0',
    packages = ['shellexample'],
    package_data = {'shellexample': ['htdocs/*.css']},

    author = 'moo',
    description = '',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    license = 'BSD',
    keywords = 'trac plugin macro',
    url = 'http://trac-hacks.org/wiki/ShellExampleMacro',
    download_url = 'http://trac-hacks.org/svn/exampleshellmacro/0.11#egg=TracShellExampleMacro-dev',
    classifiers = [
        'Framework :: Trac',
        'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    
    install_requires = ['Trac'],

    entry_points = {
        'trac.plugins': [
            'shellexample.macro = shellexample.macro',
        ]
    },
)
