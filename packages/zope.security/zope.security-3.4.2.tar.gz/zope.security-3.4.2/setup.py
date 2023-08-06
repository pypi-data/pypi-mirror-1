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

$Id: setup.py 98322 2009-03-23 13:04:07Z voblia $
"""
import os
from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.security',
      version = '3.4.2',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Zope3 Security Architecture',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '======================'
          + '\n\n' +
          read('src', 'zope', 'security', 'README.txt')
          + '\n\n' +
          read('src', 'zope', 'security', 'untrustedinterpreter.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "security",
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
      url='http://cheeseshop.python.org/pypi/zope.security',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      ext_modules=[Extension("zope.security._proxy",
                             [os.path.join('src', 'zope', 'security',
                                           "_proxy.c")
                              ], include_dirs=['include']),
                   Extension("zope.security._zope_security_checker",
                             [os.path.join('src', 'zope', 'security',
                                           "_zope_security_checker.c")
                              ]),
                   ],
      install_requires=['setuptools',
                        'pytz',
                        'zope.component',
                        'zope.configuration',
                        'zope.deferredimport',
                        'zope.exceptions',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.location',
                        'zope.proxy >= 3.4.2',
                        'zope.thread',
                        'zope.schema',
                        ],
      extras_require = dict(
          untrustedpython=["RestrictedPython"]
          ),
      include_package_data = True,
      zip_safe = False,
      )
