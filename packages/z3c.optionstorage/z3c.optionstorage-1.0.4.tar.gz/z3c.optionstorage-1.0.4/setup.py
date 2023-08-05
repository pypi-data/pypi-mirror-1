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
"""Setup for z3c.viewlet package

$Id: setup.py 81425 2007-11-03 05:51:06Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='z3c.optionstorage',
      version = '1.0.4',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Optional Storages -- Persistent, Managable Vocabularies',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 vocabulary zodb managable",
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
      url='http://cheeseshop.python.org/pypi/z3c.optionstorage',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      extras_require=dict(test=['zope.testing']),
      install_requires = ['setuptools',
                          'ZODB3',
                          'zope.annotation',
                          'zope.configuration',
                          'zope.deprecation',
                          'zope.i18n',
                          'zope.interface',
                          'zope.proxy',
                          'zope.app.schema',
                          'zope.schema',
                          'zope.security',
                          'zope.app.pagetemplate',
                          'zope.app.publisher',
                          'zope.app.form',
                          'zope.app.zapi'],
      include_package_data = True,
      zip_safe = False,
      )
