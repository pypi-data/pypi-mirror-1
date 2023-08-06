##############################################################################
# Copyright (c) 2008 David Pratt
# All Rights Reserved.
# Copyright (c) 2008 Agendaless Consulting and Contributors
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Distutils setup
"""

from setuptools import setup, find_packages
import os

def read(*rnames):
    try:
        return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    except:
        return open(os.path.join(os.getcwd(), *rnames)).read()

__version__ = '1.0a3'

name = 'repoze.cssutils'

requires = ['setuptools',
            'nose',
           ]

setup(name=name,
      version=__version__,
      description = 'CSS parsing and utilities',
      long_description=(read('README.txt')+'\n\n'+read('CHANGES.txt')),
      keywords = "css repoze parsing",
      author = "David Pratt",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (refer to /docs/LICENSE.txt)",
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules',      
          ],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages = ['repoze'],
      install_requires=requires,
      tests_require=requires,
      test_suite='nose.collector',
      include_package_data = True,
      zip_safe = False,
     )

