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
"""Setup for zope.app.zptpage package

$Id: setup.py 74483 2007-04-22 10:54:52Z ctheune $
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.zptpage',
      version = '3.4.0a1',
      url='http://svn.zope.org/zope.app.zptpage',
      license='ZPL 2.1',
      description='Zope zptpage',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles']),
      install_requires=['setuptools',
                        'zope.app.container',
                        'zope.app.pagetemplate',
                        'zope.app.publication',
                        'zope.filerepresentation',
                        'zope.formlib',
                        'zope.i18nmessageid',
                        'zope.index',
                        'zope.interface',
                        'zope.pagetemplate',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.size',
                        'zope.traversing',
                        'ZODB3',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
