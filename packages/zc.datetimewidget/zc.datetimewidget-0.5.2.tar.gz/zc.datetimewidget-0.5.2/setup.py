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
"""Setup for zc.datetimewidget package

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zc.datetimewidget',
      version = '0.5.2',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Javascript-based widgets for date and datetime fields.',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Dcoumentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'zc', 'datetimewidget', 'widgets.txt')
          + '\n\n' +
          read('src', 'zc', 'datetimewidget', 'demo', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 date datetime widget javascript",
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
      url='http://cheeseshop.python.org/pypi/zc.datetimewidget',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zc'],
      extras_require=dict(
          test=['zope.app.zcmlfiles',
                'zope.app.securitypolicy',
                'zope.app.authentication',
                'zope.app.server',
                'zope.securitypolicy',
                'zope.testbrowser',
                'zope.testing',
                ]),
      install_requires=['pytz',
                        'setuptools',
                        'zc.i18n',
                        'zc.resourcelibrary',
                        'zope.app.form',
                        'zope.component',
                        'zope.datetime',
                        'zope.interface',
                        'zope.publisher',
                        'zope.schema',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
