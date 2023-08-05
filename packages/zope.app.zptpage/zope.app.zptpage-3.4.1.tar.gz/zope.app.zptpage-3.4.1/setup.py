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

$Id: setup.py 81332 2007-10-31 20:05:26Z srichter $
"""

import os

from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zope.app.zptpage',
    version='3.4.1',
    url='http://pypi.python.org/pypi/zope.app.zptpage',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Framework :: Zope3',
        ],
    description='ZPT page content component',
    long_description = (
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zope', 'zope.app'],
    include_package_data=True,
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
    extras_require=dict(test=['zope.app.testing',
                              'zope.app.securitypolicy',
                              'zope.app.zcmlfiles']),
    zip_safe=False,
    )
