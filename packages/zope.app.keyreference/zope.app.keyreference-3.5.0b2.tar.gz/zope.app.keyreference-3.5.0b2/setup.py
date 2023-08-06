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
"""Setup for zope.app.keyreference package

$Id: setup.py 89860 2008-08-15 03:31:47Z asmith $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'zope.app.keyreference',
      version = '3.5.0b2',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Key References',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Dcoumentation\n' +
          '----------------------\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'keyreference', 'persistent.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 key reference persistent",
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
      url='http://cheeseshop.python.org/pypi/zope.app.persistent',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      install_requires = ['setuptools',
                          'ZODB3',
                          'zope.component',
                          'zope.i18nmessageid',
                          'zope.interface',
                          'zope.schema',
                          'zope.testing',
                          ],
      include_package_data = True,
      zip_safe = False,
      )
