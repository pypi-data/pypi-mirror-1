##############################################################################
#
# Copyright (c) 2004-2007 Zope Corporation and Contributors.
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
"""Setup for zope.interface package

$Id: setup.py 80479 2007-10-02 12:11:37Z jim $
"""

import os, sys

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

    if sys.version_info[:2] >= (2, 4):
        extra = dict(
            package_data={
                'zope.interface': ['*.txt'],
                'zope.interface.tests': ['*.txt'],
                }
            )
    else:
        extra = {}

else:
    extra = dict(
        namespace_packages=["zope"],
        include_package_data = True,
        zip_safe = False,
        tests_require = ['zope.testing'],
        install_requires = ['setuptools'],
        )

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zope', 'interface', 'README.txt')
        + '\n' +
        read('src', 'zope', 'interface', 'adapter.txt')
        + '\n' +
        read('src', 'zope', 'interface', 'human.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        )

open('documentation.txt', 'w').write(long_description)

setup(name='zope.interface',
      version = '3.4.1',
      url='http://www.python.org/pypi/zope.interface',
      license='ZPL 2.1',
      description='Zope 3 Interface Infrastructure',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description=long_description,

      packages = ['zope', 'zope.interface'],
      package_dir = {'': 'src'},
      ext_package='zope.interface',
      ext_modules=[Extension("_zope_interface_coptimizations",
                             [os.path.join('src', 'zope', 'interface',
                                           "_zope_interface_coptimizations.c")
                              ]),
                   ],
      **extra)
