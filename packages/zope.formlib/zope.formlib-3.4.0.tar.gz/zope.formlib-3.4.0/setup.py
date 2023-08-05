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
"""Setup for zope.formlib package

$Id: setup.py 80316 2007-09-28 12:11:52Z philikon $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.formlib',
      version = '3.4.0',
      url='http://pypi.python.org/pypi/zope.formlib',
      license='ZPL 2.1',
      description='Form generation and validation library for Zope',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description=(read('README.txt')
                        + '\n\n' +
                        read('CHANGES.txt')
                        + '\n\n' +
                        read('src', 'zope', 'formlib', 'form.txt')
                        + '\n\n' +
                        read('src', 'zope', 'formlib', 'errors.txt')
                        + '\n\n' +
                        read('src', 'zope', 'formlib', 'namedtemplate.txt')
                        ),

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope',],
      install_requires=['setuptools',
                        'pytz',
                        'zope.app.container',
                        'zope.app.form',
                        'zope.app.pagetemplate',
                        'zope.component',
                        'zope.deferredimport',
                        'zope.event',
                        'zope.i18n',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.lifecycleevent',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.traversing',
                        # testing requirements:
                        'zope.app.testing',
                        'zope.app.zcmlfiles',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
