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
"""
setuptools commands
"""
import os
from setuptools import Command

from runflakes import run_flake
from runtests import run_tests

class QAChecker(Command):
    """setuptools Command"""
    description = "run quality assurance tests over the package"
    user_options = []

    def initialize_options(self):
        """init options"""
        pass

    def finalize_options(self):
        """finalize options"""
        pass

    def run(self):
        """runner"""
        run_flake()


class ZChecker(Command):
    """setuptools Command"""
    description = "run zope.testing test runner over the package"
    user_options = []

    def initialize_options(self):
        """init options"""
        pass

    def finalize_options(self):
        """finalize options"""
        pass

    def run(self):
        """runner"""
        if os.curdir == '.':
            top_dir = os.path.realpath(os.curdir)
        else:
            top_dir = os.curdir

        for dirpath, dirnames, filenames in os.walk(top_dir):
            for dirname in dirnames:
                if dirname in ('build', 'dist') or dirname.startswith('.'):
                    continue
                run_tests(os.path.join(top_dir, dirname))

