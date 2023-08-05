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
"""Setup for zope.app.testing package

$Id: setup.py 74465 2007-04-22 10:48:14Z ctheune $
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.testing',
      version = '3.4.0a1',
      url='http://svn.zope.org/zope.app.testing',
      license='ZPL 2.1',
      description='Zope application server testing',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require=dict(test=['zope.app.zptpage',
                                'zope.app.securitypolicy',
                                'zope.app.zcmlfiles'
                                ]),
      install_requires=['setuptools',
                        'zope.annotation',
                        'zope.app.authentication',
                        'zope.app.component',
                        'zope.app.container',
                        'zope.app.debug',
                        'zope.app.dependable',
                        'zope.app.folder',
                        'zope.app.publication',
                        'zope.app.security',
                        'zope.component',
                        'zope.deferredimport',
                        'zope.i18n',
                        'zope.interface',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.testing',
                        'zope.traversing',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
