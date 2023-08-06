#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Setup for ks.smartimage package

$Id: setup.py 35337 2008-05-28 09:01:39Z cray $
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
        read('src', 'ks', 'smartimage', 'README.txt')
    except IOError:
        return ''

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + details()
    )

setup(
    name = 'ks.smartimage',
    version = '1.2.1',
    url = 'http://code.keysolutionscorp.com/downloads/public/pypi/ks.smartimage',
    license = 'ZPL 2.1',
    description = 'Efficiently store and publish images with ks.smartimage',
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
    namespace_packages = ['ks',],
    install_requires=[x.strip() for x in open("DEPENDENCIES.txt").read().split("\n") if x.strip()],
    extras_require = dict(
        test = ['zope.testing',
                'ZODB3'],
        ),
    include_package_data = True,
    dependency_links = ['http://download.zope.org/distribution', 'http://effbot.org/downloads'],
    zip_safe = False,
    )
