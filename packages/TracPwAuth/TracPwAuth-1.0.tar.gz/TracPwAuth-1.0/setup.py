#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'TracPwAuth',
    version = '1.0',
    packages = ['pwauth'],

    author = 'Noah Kantrowitz',
    author_email = 'coderanger@yahoo.com',
    description = 'An AccountManager password store that uses pwauth to check against the system password databse.',
    license = 'BSD',
    keywords = 'trac plugin accountmanager',
    url = 'http://trac-hacks.org/wiki/PwAuthPlugin',
    classifiers = [
        'Framework :: Trac',
    ],
    
    install_requires = ['TracAccountManager'],

    entry_points = {
        'trac.plugins': [
            'pwauth.store = pwauth.store',
        ]
    },
)
