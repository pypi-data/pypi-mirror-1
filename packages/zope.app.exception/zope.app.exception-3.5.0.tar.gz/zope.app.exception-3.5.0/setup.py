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
"""Setup for zope.app.exception package

$Id: setup.py 98910 2009-04-06 09:06:21Z icemac $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '3.5.0'

setup(name='zope.app.exception',
      version=version,
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope 3 exception views',
      long_description=(
          read('README.txt')
          + '\n\n' +
          '.. contents::'
          + '\n\n' +
          read('src', 'zope', 'app', 'exception', 'browser', 'systemerror.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 exception view",
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
      url='http://pypi.python.org/pypi/zope.app.exception',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require=dict(test=[
          'zope.app.securitypolicy',
          'zope.app.testing',
          'zope.app.zcmlfiles',
          'zope.app.zptpage',
      ]),
      install_requires=['setuptools',
                        'zope.app.pagetemplate',
                        # This is a dependency we can avaid:
                        'zope.formlib',
                        'zope.interface',
                        'zope.publisher',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
