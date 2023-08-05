##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Setup for zope.documenttemplate package

$Id: setup.py 80489 2007-10-02 13:40:47Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name="zope.dottedname",
      version = '3.4.2',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Resolver for Python dotted names.',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation' +
          '----------------------'
          + '\n\n' +
          read('src', 'zope', 'dottedname', 'resolve.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = 'resolve dotted name',
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
      url='http://cheeseshop.python.org/pypi/zope.dottedname',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require = dict(
          test=['zope.testing'],
          ),
      install_requires = ['setuptools'],
      include_package_data=True,
      zip_safe = False
      )

