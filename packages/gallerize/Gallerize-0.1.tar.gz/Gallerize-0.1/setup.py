#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gallerize setup script
~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2007 Jochen Kupperschmidt
:license: MIT, see LICENSE for details.
"""

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

from gallerize import gallerize


setup(
    name = 'Gallerize',
    version = gallerize.__version__,
    description = 'Web image gallery generator',
    long_description = gallerize.__doc__,
    license = gallerize.__license__,
    author = gallerize.__author__,
    url = gallerize.__url__,
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: German',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Multimedia :: Graphics :: Presentation',
    ],
    install_requires = [
        'Genshi >= 0.4.3',
        'PIL >= 1.1.6',
    ],
    entry_points = {
        'console_scripts': [
            'gallerize = gallerize.gallerize:main',
        ],
    },
)
