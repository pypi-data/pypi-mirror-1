# -*- coding: utf-8 -*-
# Copyright (C)2007 Gael Pasgrimaud

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
This module contains the tool of svnhelper
"""
import os
from setuptools import setup, find_packages

name = 'svnhelper'
version = '0.2'

README = os.path.join(os.path.dirname(__file__),
          'src', 'svnhelper', 'README.txt')

long_description = open('README.txt').read() + '\n\n' + \
                   open('CHANGES.txt').read() + '\n\n' + \
                   open(README).read() + '\n\n'

setup(name=name,
      version=version,
      description="some svn utils to easily import/checkout packages",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='',
      license='GPL',
      packages = find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=[name],
      include_package_data=True,
      zip_safe=False,
      test_suite = "%s.tests.test_suite" % name,
      tests_require=[
          'zope.testing',
      ],
      install_requires=[
          'setuptools',
      ],
      entry_points={
          "distutils.commands": [
             "svn = %s.command:svn" % name,
             "import = %s.command:svnimport" % name,
             ],
          "console_scripts": [
             "svnh = svnhelper.script:main",
             "svnco = svnhelper.script:svnco",
             ],
          },
      )

