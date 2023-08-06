#!/usr/bin/env python
# -*- coding:utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

from bdist_debian import bdist_debian

import presenter

setup(
    name='Presenter',
    version=presenter.__version__,
    description="The presentation tool designed for control freaks.",
    url='http://flowblok.selfip.net:8001/trac/presenter/',
    author='Peter Ward',
    author_email='peteraward@gmail.com',
    license='GNU General Public License (GPL)',
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.5',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Multimedia :: Video :: Display',
    ],
    packages=[
        'presenter',
        'presenter.handlers'
    ],
    package_data={
        'presenter': ['interface.glade'],
    },
    data_files=[
        ('share/icons/hicolor/48x48/apps', ['icons/48x48/presenter.png']),
        ('share/icons/hicolor/128x128/apps', ['icons/128x128/presenter.png']),
        ('share/icons/hicolor/scalable/apps', ['icons/scalable/presenter.svg']),
        ('share/applications', ['presenter.desktop']),
    ],
    entry_points={
        'gui_scripts': [
            'presenter = presenter:main',
        ]
    },
    scripts=['scripts/presenter'],
    cmdclass={'bdist_debian': bdist_debian},
    depends="python2.5, python-gtk2 (>= 2.12), python-gobject, python-cairo, python-pkg-resources",
    recommends="python-gnome2-desktop, python-evince, python-gst0.10, python-setuptools",
)

