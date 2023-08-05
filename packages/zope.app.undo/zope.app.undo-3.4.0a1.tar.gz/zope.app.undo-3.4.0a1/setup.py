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
"""Setup for zope.app.undo package

$Id: setup.py 74471 2007-04-22 10:52:01Z ctheune $
"""

import os

from setuptools import setup, find_packages

setup(name = 'zope.app.undo',
      version = '3.4.0a1',
      url = 'http://svn.zope.org/zope.app.undo',
      license = 'ZPL 2.1',
      description = 'Zope app.undo',
      author = 'Zope Corporation and Contributors',
      author_email = 'zope3-dev@zope.org',
      long_description = "",

      packages = find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages = ['zope', 'zope.app'],
      install_requires = ['setuptools',
                          'zope.app.component',
                          'zope.app.security',
                          'zope.component',
                          'zope.interface',
                          'zope.location',
                          'zope.publisher',
                          'zope.security',
                          'zope.traversing',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing']),
      include_package_data = True,

      zip_safe = False,
      )
