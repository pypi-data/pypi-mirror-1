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

$Id: setup.py 99513 2009-04-26 13:26:48Z hannosch $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.testing',
      version = '3.6.2',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Application Testing Support',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'testing', 'dochttp.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'testing', 'doctest.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 test testing setup functional",
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
      url='http://pypi.python.org/pypi/zope.app.testing',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require=dict(test=['zope.app.authentication',
                                'zope.app.zptpage',
                                'zope.app.securitypolicy',
                                'zope.app.zcmlfiles',
                                'ZODB3',
                                'zope.publisher'
                                ]),
      install_requires=['setuptools',
                        'zope.annotation',
                        'zope.app.appsetup >=3.5.0',
                        'zope.app.component',
                        'zope.app.debug',
                        'zope.app.dependable',
                        'zope.app.publication',
                        'zope.component',
                        'zope.container',
                        'zope.i18n',
                        'zope.interface',
                        'zope.location',
                        'zope.password',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.site',
                        'zope.testing',
                        'zope.traversing',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
