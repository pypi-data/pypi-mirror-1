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
"""Setup for zope.i18nmessageid package

$Id: setup.py 73161 2007-03-14 04:48:47Z baijum $
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.i18nmessageid',
      version='3.4dev_r73161',

      url='http://svn.zope.org/zope.i18nmessageid',
      license='ZPL 2.1',
      description='Zope 3 i18n Message Identifier',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description='',

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      ext_modules=[Extension("zope.i18nmessageid._zope_i18nmessageid_message",
                             [os.path.join('src', 'zope', 'i18nmessageid',
                                           "_zope_i18nmessageid_message.c")
                              ]),
                   ],

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['setuptools'],
      include_package_data = True,

      zip_safe = False,
      )
    
