#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Peter Ward
# All rights reserved.

from setuptools import setup, find_packages

setup(
    name = "Presenter",
    version = "0.1.0",

    description = 'A standalone presentation viewer.',

    author = 'Peter Ward',
    author_email = 'peteraward@gmail.com',

    url = "http://flowblok.wordpress.com/",

    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Graphics :: Presentation',
    ],

    platforms = 'Any',
    keywords = ('presenter', 'presentation', 'opendocument', 'odf', 'odp'),

    packages = find_packages(exclude=['tests*']),

    package_data = {
        'presenter': ['*.glade'],
    },

    entry_points = {
        'gui_scripts': ['presenter = presenter:main']
    },

#    test_suite = 'tests.suite',

#    install_requires=['odfpy==0.8'],
)
