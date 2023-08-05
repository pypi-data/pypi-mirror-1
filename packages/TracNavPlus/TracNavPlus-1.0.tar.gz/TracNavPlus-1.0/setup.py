#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'TracNavPlus',
    version = '1.0',
    packages = ['navplus'],
    package_data = { 'navplus': ['templates/*.cs', 'htdocs/*.js', 'htdocs/*.css' ] },

    author = 'Noah Kantrowitz',
    author_email = 'coderanger@yahoo.com',
    description = 'Enhanced control over the navigation bars.',
    license = 'BSD',
    keywords = 'trac plugin',
    url = 'http://trac-hacks.org/wiki/NavPlusPlugin',
    classifiers = [
        'Framework :: Trac',
    ],
    
    install_requires = ['TracWebAdmin'],

    entry_points = {
        'trac.plugins': [
            'navplus.filter = navplus.filter',
            'navplus.admin = navplus.admin',
        ]
    },
)
