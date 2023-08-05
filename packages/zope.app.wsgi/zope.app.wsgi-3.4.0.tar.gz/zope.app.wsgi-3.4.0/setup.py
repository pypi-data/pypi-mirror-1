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
"""Setup for zope.app.wsgi package

$Id: setup.py 79644 2007-09-14 17:01:11Z philikon $
"""
from setuptools import setup, find_packages, Extension

setup(name='zope.app.wsgi',
      version = '3.4.0',
      url='http://pypi.python.org/pypi/zope.app.wsgi',
      license='ZPL 2.1',
      description='WSGI application for the zope.publisher',
      long_description=open('README.txt').read(),
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles',
                                  'zope.testbrowser']),
      install_requires=['setuptools',
                        'ZConfig',
                        'zope.app.appsetup',
                        'zope.app.publication',
                        'zope.app.wsgi',
                        'zope.event',
                        'zope.interface',
                        'zope.publisher',
                        'zope.security',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
