##############################################################################
#
# Copyright (c) 2008 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__version__ = '0.3'

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

_boundary = '\n' + ('-' * 60) + '\n\n'

setup(name='dataflake.ldapconnection',
      version=__version__,
      description='LDAP connection library',
      long_description=( read('README.txt') 
                       + _boundary 
                       + read('CHANGES.txt')
                       + _boundary 
                       + "Download\n========"
                       ),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
        ],
      keywords='ldap ldapv3',
      author="Agendaless Consulting and Jens Vagelpohl",
      url="http://pypi.python.org/pypi/dataflake.ldapconnection",
      license="ZPL 2.1 (http://www.zope.org/Resources/License/ZPL-2.1)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['dataflake'],
      zip_safe=False,
      tests_require = [
              'python-ldap',
              ],
      install_requires=[
              'python-ldap'
              ],
      test_suite='dataflake.ldapconnection.tests',
      )

