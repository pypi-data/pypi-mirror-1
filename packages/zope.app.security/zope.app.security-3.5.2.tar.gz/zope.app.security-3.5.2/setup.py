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

$Id: setup.py 89100 2008-07-31 16:08:57Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.security',
      version = '3.5.2',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Security Components for Zope 3 Applications',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Dcoumentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'security', 'globalprincipals.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'security', 'logout.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'security', 'browser',
               'authutilitysearchview.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'security', 'browser', 'loginlogout.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'security', 'browser',
               'principalterms.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 security authentication principal ftp http",
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
      url='http://cheeseshop.python.org/pypi/zope.app.security',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require=dict(test=['zope.app.testing']),
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
