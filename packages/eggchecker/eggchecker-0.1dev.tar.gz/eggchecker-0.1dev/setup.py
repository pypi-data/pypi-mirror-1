#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2007 Tarek Ziadé
#
# Authors:
#   Tarek Ziadé <tarek@ziade.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
from setuptools import setup, find_packages
import sys, os

version = '0.1'

README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='eggchecker',
      version=version,
      description=("setuptools command extensions to run QA and tests "
                   "on the code"),
      long_description=README,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='qa pylintrc',
      author='Tarek Ziade',
      author_email='tarek@ziade.org',
      url='http://hg.programmation-python.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'pyflakes>=0.2.1,==dev'
      ],
      entry_points = {
        "distutils.commands": [
                    "qa = eggchecker:QAChecker",
                    "ztest = eggchecker:ZChecker"
                            ],
     },

      )
