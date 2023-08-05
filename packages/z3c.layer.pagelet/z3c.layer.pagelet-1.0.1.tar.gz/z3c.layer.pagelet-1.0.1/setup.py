#!python
##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup

$Id:$
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return xml.sax.saxutils.escape(text)

setup(
    name = 'z3c.layer.pagelet',
    version = '1.0.1',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    description = "Pagelet layer setup for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n'
        '**********************'
        + '\n\n' +
        read('src', 'z3c', 'layer', 'pagelet', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    keywords = "z3c pagelet layer zope zope3",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://pypi.python.org/pypi/z3c.layer.pagelet',
    license='ZPL 2.1',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'zope.testbrowser',
            'zope.app.securitypolicy',
            'zope.app.testing',
            'zope.app.zcmlfiles',
            'zope.app.twisted',
            'zope.viewlet',
            'z3c.pagelet',
            'zc.configuration',
            ],
        ),
    install_requires = [
        'setuptools',
        'zope.configuration',
        'zope.traversing',
        'zope.app.http',
        'zope.app.publisher',
        ],
    zip_safe = False,
)

