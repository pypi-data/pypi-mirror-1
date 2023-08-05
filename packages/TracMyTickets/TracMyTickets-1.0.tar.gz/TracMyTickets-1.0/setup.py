#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'TracMyTickets',
    version = '1.0',
    packages = ['mytickets'],
    #package_data = { 'mytickets': ['templates/*.cs', 'htdocs/*.js', 'htdocs/*.css' ] },

    author = 'Noah Kantrowitz',
    author_email = 'coderanger@yahoo.com',
    description = 'A simple macro to show your tickets.',
    license = 'BSD',
    keywords = 'trac plugin macro tickets query',
    url = 'http://trac-hacks.org/wiki/MyTicketsPlugin',
    classifiers = [
        'Framework :: Trac',
    ],
    
    install_requires = [],

    entry_points = {
        'trac.plugins': [
            'mytickets.macro = mytickets.macro',
        ]
    },
)
