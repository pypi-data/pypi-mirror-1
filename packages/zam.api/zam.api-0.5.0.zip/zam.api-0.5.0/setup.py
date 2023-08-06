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
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='zam.api',
    version='0.5.0',
    author = "Stephan Richter, Roger Ineichen and the Zope Community",
    author_email = "zope3-dev@zope.org",
    description = "API for ZAM (Zope Application Management",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c zam api",
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
    url = 'http://cheeseshop.python.org/pypi/zam.api',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zam'],
    extras_require = dict(
        test = [
            'z3c.baseregistry',
            'z3c.zrtresource',
            'zope.annotation',
            'zope.app.component',
            'zope.app.intid',
            'zope.app.securitypolicy',
            'zope.app.server',
            'zope.app.testing',
            'zope.app.twisted',
            'zope.testbrowser',
            'zope.testing',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.baseregistry',
        'z3c.breadcrumb',
        'z3c.form',
        'z3c.formui',
        'z3c.layer.ready2go',
        'z3c.menu.ready2go',
        'z3c.pagelet',
        'z3c.template',
        'zc.configuration',
        'zope.app.renderer',
        'zope.component',
        'zope.contentprovider',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.viewlet',
        ],
    zip_safe = False,
)
