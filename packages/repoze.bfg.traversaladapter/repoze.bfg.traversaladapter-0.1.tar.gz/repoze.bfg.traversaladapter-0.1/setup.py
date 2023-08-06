##############################################################################
#
# Copyright (c) 2008 Agendaless Consulting and Contributors.
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

__version__ = '0.1'

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'repoze.bfg',
    'zope.interface',
    'zope.testing',
    ]

setup(name='repoze.bfg.traversaladapter',
      version=__version__,
      description=('Alternative model graph traverser for the repoze.bfg web '
                   'framework which allows registering arbitrary '
                   'adapters for the type or interface of model '
                   'objects encountered during traversal.'),
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
      keywords='bfg repoze.bfg traverser traversal adapter',
      author="F. Oliver Gathmann",
      author_email="gathmann@ocelerate.org",
      url="http://packages.python.org/repoze.bfg.traversaladapter",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze', 'repoze.bfg'],
      zip_safe=False,
      tests_require = requires,
      install_requires = requires,
      test_suite="repoze.bfg.traversaladapter",
      entry_points = """\
      """
      )
