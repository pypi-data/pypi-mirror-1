# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
version = open(os.path.join(here, 'VERSION.txt')).readline().rstrip()

setup(name='repoze.who-testutil',
      version=version,
      description=('Test utilities for repoze.who-powered applications'),
      long_description=README,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security"
        ],
      keywords='web application wsgi authentication testing tests repoze',
      author='Gustavo Narea',
      author_email='repoze-dev@lists.repoze.org',
      namespace_packages = ['repoze', 'repoze.who', 'repoze.who.plugins'],
      url='http://code.gustavonarea.net/repoze.who-testutil/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      tests_require=['repoze.who >= 1.0', 'coverage', 'nose'],
      install_requires=[
        'repoze.who >= 1.0',
        'zope.interface',
        'Paste > 1.7', # Workaround for the buggy setuptools
        'PasteDeploy >= 1.3.3'],
      test_suite='nose.collector',
      entry_points = """\
      """
      )
