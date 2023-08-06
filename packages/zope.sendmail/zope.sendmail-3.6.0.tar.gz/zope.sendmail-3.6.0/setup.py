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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.sendmail package

$Id: setup.py 103980 2009-09-14 21:50:55Z gary $
"""
from setuptools import setup, find_packages


setup(name='zope.sendmail',
      version = '3.6.0',
      url='http://pypi.python.org/pypi/zope.sendmail',
      license='ZPL 2.1',
      description='Zope sendmail',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description='\n\n'.join([
          open('README.txt').read(),
          open('CHANGES.txt').read(),
          ]),

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['setuptools',
                        'transaction',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.schema',

                        # XXX: maybe the following should moved into
                        # extras to ease reusability.

                        # it's only needed for vocabulary and zcml
                        'zope.component',

                        # these are only needed for zcml
                        'zope.configuration',
                        'zope.security',

                       ],
      include_package_data = True,
      zip_safe = False,
      )
