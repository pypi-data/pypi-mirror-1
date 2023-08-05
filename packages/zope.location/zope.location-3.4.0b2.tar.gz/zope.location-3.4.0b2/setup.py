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
"""Setup for zope.location package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name='zope.location',
      version = '3.4.0b2',
      url='http://pypi.python.org/pypi/zope.location/',
      license='ZPL 2.1',
      description='Zope Location',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="In Zope3, location are special objects"
                       "that has a structural location.",

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope',],
      extras_require=dict(test=['zope.app.container']),
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.schema',
                        'zope.proxy>3.3',
                        'zope.security',
                        'zope.traversing',
                        ],
      include_package_data = True,

      zip_safe = False,
      )
