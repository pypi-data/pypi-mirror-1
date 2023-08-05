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
"""Setup for zope.app.externaleditor package

$Id: setup.py 81512 2007-11-05 03:40:21Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.externaleditor',
      version = '3.4.0',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Editing Zope 3 Content with an External Editor',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 external editor",
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
      url='http://cheeseshop.python.org/pypi/zope.app.externaleditor',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require=dict(
          test=['zope.app.testing',
                ]),
      install_requires = [
          'setuptools',
          'zope.app.component',
          'zope.app.container',
          'zope.app.content',
          'zope.app.file',
          'zope.app.interface',
          'zope.app.testing',
          'zope.app.zapi',
          'zope.filerepresentation',
          'zope.interface',
          'zope.publisher',
          'zope.security',
          'zope.traversing',
          ],
      include_package_data = True,
      zip_safe = False,
      )
