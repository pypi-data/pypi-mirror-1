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
"""Setup for zope.container package

$Id: setup.py 97995 2009-03-12 16:17:19Z nadako $
"""
import os
from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.container',
      version = '3.7.2',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Container',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n'
          '**********************\n'
          + '\n\n' +
          read('src', 'zope', 'container', 'constraints.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 container",
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
      url='http://pypi.python.org/pypi/zope.container',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      ext_modules=[Extension("zope.container._zope_container_contained",
                             [os.path.join("src", "zope", "container",
                                           "_zope_container_contained.c")
                              ], include_dirs=['include']),
                   ],
      extras_require=dict(
          test=['zope.copypastemove']),
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.cachedescriptors',
                        'zope.dottedname',
                        'zope.schema',
                        'zope.component',
                        'zope.event',
                        'zope.location',
                        'zope.security',
                        'zope.lifecycleevent',
                        'zope.i18nmessageid',
                        'zope.filerepresentation',
                        'zope.size',
                        'zope.traversing',
                        'zope.publisher',
                        'zope.broken',
                        'zope.app.dependable',
                        'ZODB3',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
