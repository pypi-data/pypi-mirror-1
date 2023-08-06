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
"""Setup for zope.traversing package

$Id: setup.py 89054 2008-07-30 18:01:21Z mgedmin $
"""
from setuptools import setup, find_packages

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.traversing',
      version = '3.4.1',
      url='http://pypi.python.org/pypi/zope.traversing',
      license='ZPL 2.1',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description="Resolving paths in the object hierarchy",
      long_description=long_description,

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope',],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles',
                                  'zope.app.zptpage']),
      install_requires=['setuptools',
                        'zope.app.applicationcontrol',
                        'zope.component',
                        'zope.i18n',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.proxy',
                        'zope.publisher',
                        'zope.security',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
