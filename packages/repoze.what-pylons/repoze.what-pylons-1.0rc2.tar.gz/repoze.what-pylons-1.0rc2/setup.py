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

setup(name='repoze.what-pylons',
      version=version,
      description=('The repoze.what v1 plugin for Pylons/TG2 integration'),
      long_description=README,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Pylons",
        "Framework :: TurboGears",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security"
        ],
      keywords='web application wsgi server pylons turbogears ' \
               'authorization repoze',
      author='Gustavo Narea',
      author_email='repoze-dev@lists.repoze.org',
      namespace_packages = ['repoze', 'repoze.what', 'repoze.what.plugins'],
      url='http://code.gustavonarea.net/repoze.what-pylons/',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      tests_require=[
          'repoze.what',
          'coverage',
          'nose',
          'Pylons',
          'TurboGears2 >= 2.0b5',
          ],
      install_requires=[
          'repoze.what >= 1.0.4',
          'Pylons >= 0.9.7rc4',
          'decorator >= 3.0',
          ],
      test_suite='nose.collector',
      entry_points = """\
      """
      )
