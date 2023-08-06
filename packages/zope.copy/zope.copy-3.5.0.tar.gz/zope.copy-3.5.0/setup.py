##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Setup for zope.copy package

$Id: setup.py 96280 2009-02-08 22:27:11Z nadako $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'zope.copy',
      version = '3.5.0',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      description='Pluggable object copying mechanism',
      long_description=(
          read('src', 'zope', 'copy', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 copying cloning",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Framework :: Zope3',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Database',
          ],
      url='http://pypi.python.org/pypi/zope.copy',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require={'test': ['zope.component',
                               'zope.location',
                               'zope.testing']},
      install_requires = ['setuptools',
                          'zope.interface',
                          ],
      include_package_data = True,
      zip_safe = False,
      )
