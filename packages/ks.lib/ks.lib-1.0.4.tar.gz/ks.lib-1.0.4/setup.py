#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Setup for ks.lib package

$Id: setup.py 35349 2008-10-24 09:01:22Z anatoly $
"""

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def details():
    try:
        return '\n' + \
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' + \
        read('src', 'ks', 'hivurtskin', 'README.txt')
    except IOError:
        return ''

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + details()
    )

setup(
    name = 'ks.lib',
    version = '1.0.4',
    url = 'http://code.keysolutionscorp.com/downloads/public/pypi/ks.lib',
    license = 'ZPL 2.1',
    description = 'Some useful modules for Hivurt',
    author = 'Key Solutions Development TEAM',
    author_email = 'ksd-team@keysolutions.ru',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Framework :: Zope3',
        ],
    long_description = long_description,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['ks', 'ks.lib'],
    install_requires=[x.strip() for x in open("DEPENDENCIES.txt").read().split("\n") if x.strip()],
    extras_require = dict(
        test = ['zope.testing',
                'ZODB3'],
        ),
    include_package_data = True,
    zip_safe = False,
    )
