##############################################################################
#
# Copyright (c) 2006-2009 Zope Corporation and Contributors.
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
"""Setup for zope.formlib package

$Id: setup.py 100110 2009-05-18 20:03:57Z icemac $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '3.6.0'

setup(name='zope.formlib',
      version=version,
      url='http://pypi.python.org/pypi/zope.formlib',
      license='ZPL 2.1',
      description='Form generation and validation library for Zope',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description=(read('README.txt')
                        + '\n\n' +
                        read('CHANGES.txt')
                        + '\n\n' +
                        read('src', 'zope', 'formlib', 'form.txt')
                        + '\n\n' +
                        read('src', 'zope', 'formlib', 'errors.txt')
                        ),
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope',],
      extras_require=dict(
          test=['zope.app.testing', 'zope.app.zcmlfiles']
          ),
      install_requires=['setuptools',
                        'pytz',
                        'zope.app.form',
                        'zope.app.pagetemplate>=3.6.0',
                        'zope.component',
                        'zope.event',
                        'zope.i18n',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.lifecycleevent',
                        'zope.publisher',
                        'zope.schema>=3.5.1',
                        'zope.security',
                        'zope.traversing',
                        'zope.browser>=1.1',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
