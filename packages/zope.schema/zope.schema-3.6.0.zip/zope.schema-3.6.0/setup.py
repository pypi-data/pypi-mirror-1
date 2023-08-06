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
"""Setup for zope.schema package

$Id: setup.py 106866 2009-12-22 14:08:19Z hannosch $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.schema',
      version = '3.6.0',
      url='http://pypi.python.org/pypi/zope.schema',
      license='ZPL 2.1',
      description='zope.interface extension for defining data schemas',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description=(read('src', 'zope', 'schema', 'README.txt')
                        + '\n\n' +
                        read('src', 'zope', 'schema', 'fields.txt')
                        + '\n\n' +
                        read('src', 'zope', 'schema', 'sources.txt')
                        + '\n\n' +
                        read('src', 'zope', 'schema', 'validation.txt')
                        + '\n\n' +
                        read('CHANGES.txt')),
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope',],
      extras_require={'test': ['zope.testing'],
                      'docs': ['z3c.recipe.sphinxdoc']},
      install_requires=['setuptools',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.event',
                       ],
      include_package_data = True,
      zip_safe = False,
      )
