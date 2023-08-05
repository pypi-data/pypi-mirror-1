# -*- coding: utf-8 -*-
# Copyright (C)2007 'Gael Pasgrimaud'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
This module contains the tool of gp.svndevelop
"""
import os
from setuptools import setup, find_packages

version = '0.2'

README = os.path.join(os.path.dirname(__file__),
                      'gp', 'svndevelop', 'README.txt')
CHANGES = os.path.join(os.path.dirname(__file__),
                      'CHANGES')

long_description = """%s

Changes
=======

%s

Download
========

""" % (open(README).read(), open(CHANGES).read())

tests_require = [
        'svnhelper',
        'zope.testing',
        'zc.buildout',
    ]

setup(name='gp.svndevelop',
      version=version,
      description="ZC buildout extension to checkout develop eggs",
      long_description=long_description,
      classifiers=[
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        ],
      keywords='buildout extension svn develop',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://pypi.python.org/pypi/gp.svndevelop',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gp'],
      include_package_data=True,
      zip_safe=False,
      test_suite = "gp.svndevelop.tests.test_suite",
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      install_requires=[
          'setuptools',
          'zc.buildout',
      ],
      entry_points = {'zc.buildout.extension':
                     ['default = gp.svndevelop:install']
                      },
      )

