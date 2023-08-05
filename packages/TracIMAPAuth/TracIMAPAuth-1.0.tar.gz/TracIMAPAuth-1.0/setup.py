#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'TracIMAPAuth',
    version = '1.0',
    packages = ['imapauth'],

    author = 'Noah Kantrowitz',
    author_email = 'coderanger@yahoo.com',
    description = 'An AccountManager password store that uses imaplib to check against an IMAP server.',
    license = 'BSD',
    keywords = 'trac plugin accountmanager',
    url = 'http://trac-hacks.org/wiki/IMAPAuthPlugin',
    classifiers = [
        'Framework :: Trac',
    ],
    
    install_requires = ['TracAccountManager'],

    entry_points = {
        'trac.plugins': [
            'imapauth.store = imapauth.store',
        ],
    },
)
