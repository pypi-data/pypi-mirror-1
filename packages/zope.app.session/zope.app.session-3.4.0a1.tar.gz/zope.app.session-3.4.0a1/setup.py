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
"""Setup for zope.app.session package

$Id: setup.py 74459 2007-04-22 10:46:47Z ctheune $
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.session',
      version = '3.4.0a1',
      url='http://svn.zope.org/zope.app.session',
      license='ZPL 2.1',
      description='Zope session',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.zptpage',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles']),
      install_requires=['setuptools',
                        'ZODB3',
                        'zope.annotation',
                        'zope.app.appsetup',
                        'zope.app.http',
                        'zope.component',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.location',
                        'zope.publisher',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
