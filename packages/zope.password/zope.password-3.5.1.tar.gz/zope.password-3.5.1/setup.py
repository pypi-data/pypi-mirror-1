##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Setup for zope.password package

$Id: setup.py 98100 2009-03-14 17:05:31Z nadako $
"""
from setuptools import setup, find_packages


setup(name='zope.password',
      version='3.5.1',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Password encoding and checking utilities',
      long_description=(
        open('README.txt').read()
        + '\n\n' +
        open('CHANGES.txt').read()
        ),
      url='http://pypi.python.org/pypi/zope.password',
      license='ZPL 2.1',
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
      keywords='zope authentication password',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      extras_require=dict(vocabulary=['zope.component', 'zope.schema'],
                          test=['zope.testing', 'zope.component', 'zope.schema'],
                          ),
      namespace_packages=['zope'],
      install_requires=['setuptools',
                        'zope.interface',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
