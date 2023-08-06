##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
"""
$Id:$
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='p01.zmi',
    version='0.5.0',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "Simple zope application management skin setup for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "Zope3 z3c p01 ZAM skin setup",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://cheeseshop.python.org/pypi/p01.zmi',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01'],
    extras_require=dict(
        test=[
            'z3c.testing',
            'zope.testing',
            'zope.site',
            'zope.annotation',
            'zope.app.component',
            'zope.app.intid',
            'zope.app.securitypolicy',
            'zope.app.server',
            'zope.app.testing',
            'zope.app.twisted',
            'zope.testbrowser',
            'zope.testing',
            ]),
    install_requires = [
        'setuptools',
        'z3c.breadcrumb',
        'z3c.form',
        'z3c.formui',
        'z3c.pagelet',
        'z3c.table',
        'z3c.tabular',
        'z3c.template',
        'z3c.contents',
        'z3c.json',
        'z3c.jsonrpc',
        'z3c.jsontree',
        'z3c.layer.pagelet',
        'z3c.layer.ready2go',
        'z3c.menu.ready2go',
        'z3c.zrtresource',
        'zope.app.component',
        'zope.app.container',
        'zope.app.generations',
        'zope.app.publication',
        'zope.component',
        'zope.configuration',
        'zope.i18n',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.traversing',
        ],
    zip_safe = False,
    )
