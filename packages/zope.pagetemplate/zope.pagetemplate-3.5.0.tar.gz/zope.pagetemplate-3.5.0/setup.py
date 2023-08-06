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
"""Setup for zope.pagetemplate package

$Id: setup.py 100367 2009-05-25 19:07:10Z tseaver $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.pagetemplate',
      version = '3.5.0',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Page Templates',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '----------------------'
          + '\n\n' +
          read('src', 'zope', 'pagetemplate', 'architecture.txt')
          + '\n\n' +
          read('src', 'zope', 'pagetemplate', 'readme.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 page template",
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
      url='http://pypi.python.org/pypi/zope.pagetemplate',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require = dict(
          test=['zope.testing',
                'zope.component',
                'zope.proxy',
                'zope.traversing',
                'zope.security',
                'RestrictedPython',
                ]),
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.tales',
                        'zope.tal',
                       ],
      include_package_data = True,
      zip_safe = False,
      )
