# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 by Gustavo Narea <http://gustavonarea.net/>
#
# This file is part of PyACL <http://code.gustavonarea.net/pyacl/>
#
# PyACL is freedomware: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or any later version.
#
# PyACL is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyACL. If not, see <http://www.gnu.org/licenses/>.

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
version = open(os.path.join(here, 'VERSION.txt')).readline().rstrip()

setup(name='PyACL',
      version=version,
      description=('Access Control List (ACL)'),
      long_description=README,
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries",
        ],
      keywords='authorization acl acls access control',
      author="Gustavo Narea",
      author_email="me@gustavonarea.net",
      namespace_packages = ['acl',],
      url="http://code.gustavonarea.net/pyacl/",
      license="GNU Affero General Public License v3 (http://www.gnu.org/licenses/agpl.html)",
      packages=find_packages('src', exclude=['tests']),
      package_dir={'': 'src'},
      package_data={
        '': ['VERSION.txt', 'README.txt'],
        'docs': ['Makefile', 'conf.py', '**.rst', '_templates/*', '_static/*']},
      exclude_package_data={'': ['README.txt', 'docs']},
      include_package_data=True,
      zip_safe=False,
      tests_require = ['coverage', 'nose'],
      install_requires=[''],
      test_suite="nose.collector",
      entry_points = """\
      """
      )

