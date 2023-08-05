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
"""Setup for zope.security package

$Id: setup.py 78854 2007-08-15 15:10:38Z jim $
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.security',
      version = '3.4.0b5',
      url='http://svn.zope.org/zope.security',
      license='ZPL 2.1',
      description='Zope3 Security Architecture',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description='The Security framework provides a generic mechanism '
                       'to implement security policies on Python objects.',

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      ext_modules=[Extension("zope.security._proxy",
                             [os.path.join('src', 'zope', 'security',
                                           "_proxy.c")
                              ], include_dirs=['include']),
                   Extension("zope.security._zope_security_checker",
                             [os.path.join('src', 'zope', 'security',
                                           "_zope_security_checker.c")
                              ]),
                   ],
      namespace_packages=['zope',],
      install_requires=['setuptools',
                        'pytz',
                        'zope.component',
                        'zope.configuration',
                        'zope.deferredimport', 
                        'zope.exceptions',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.location>=3.4.0b1.dev-r75152',
                        'zope.proxy',
                        'zope.schema',
                        ],
      include_package_data = True,
      extras_require = {'untrustedpython': ["RestrictedPython"]},
      zip_safe = False,
      )
