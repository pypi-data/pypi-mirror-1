##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Setup for zope.securitypolicy package

$Id: setup.py 102198 2009-07-24 06:18:13Z srichter $
"""

import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.securitypolicy',
    version = '3.6.1',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    description='Default security policy for Zope3',
    long_description=(
        read('README.txt')
        + '\n.. contents::\n\n' +
        read('src', 'zope', 'securitypolicy', 'zopepolicy.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    keywords="zope3 security policy",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://pypi.python.org/pypi/zope.securitypolicy',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zope'],
    install_requires=[
        'setuptools',
        'ZODB3',
        'zope.annotation',
        'zope.authentication',
        'zope.component',
        'zope.configuration',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.location',
        'zope.schema',
        'zope.security',
        ],
    include_package_data=True,
    zip_safe=False,
    )
