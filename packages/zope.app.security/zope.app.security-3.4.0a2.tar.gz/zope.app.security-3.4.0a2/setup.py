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
"""Setup for zope.app.security package

$Id: setup.py 80978 2007-10-23 22:35:00Z fdrake $
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.security',
      version = '3.4.0a2',
      url='http://svn.zope.org/zope.app.security',
      license='ZPL 2.1',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
	  packages=find_packages('src'),
	  package_dir = {'': 'src'},
      extras_require=dict(test=['zope.app.testing']),
      namespace_packages=['zope', 'zope.app'],
      install_requires=['setuptools',
                        'zope.app.authentication',
                        'zope.app.component',
                        'zope.app.container',
                        'zope.app.form',
                        'zope.app.pagetemplate',
                        'zope.app.publisher',
                        'zope.component',
                        'zope.configuration',
                        'zope.deferredimport',
                        'zope.deprecation',
                        'zope.i18n',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.location',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'ZODB3',
                        ],
      include_package_data = True,

      zip_safe = False,
      )
