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
"""Setup for zope.cachedescriptors package

$Id: setup.py 75059 2007-05-03 16:31:16Z ctheune $
"""

import os

from setuptools import setup, find_packages

setup(name='zope.cachedescriptors',
      version='3.4.0b1dev_r75668',
      url='http://svn.zope.org/zope.cachedescriptors',
      license='ZPL 2.1',
      description='Zope3 Cached Descriptors',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description='Cached descriptors cache their output.  They take '
                       'into account instance attributes that they depend on, '
                       'so when the instance attributes change, the '
                       'descriptors will change the values they return.',

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['setuptools',
                        'ZODB3'],    # persistent
      include_package_data = True,

      zip_safe = False
      )
