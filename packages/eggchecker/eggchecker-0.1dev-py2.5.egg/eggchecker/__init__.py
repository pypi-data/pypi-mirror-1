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
import compiler, sys
import os
from pyflakes import Checker as FlakeChecker
from setuptools import Command

def check(code_string, filename):
    """checks a code string"""
    try:
        tree = compiler.parse(code_string)
    except (SyntaxError, IndentationError):
        value = sys.exc_info()[1]
        try:
            (lineno, offset, line) = value[1][1:]
        except IndexError:
            print >> sys.stderr, 'could not compile %r' % (filename,)
            return 1
        if line.endswith("\n"):
            line = line[:-1]
        print >> sys.stderr, '%s:%d: could not compile' % (filename, lineno)
        print >> sys.stderr, line
        print >> sys.stderr, " " * (offset-2), "^"
        return 1
    else:
        w = FlakeChecker(tree, filename)
        w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        for warning in w.messages:
            print warning
        return len(w.messages)

def check_path(filename):
    """checks code in a path"""
    if os.path.exists(filename):
        return check(file(filename, 'U').read(), filename)

def run_flake():
    """run flake over the whole directory"""
    warnings = 0

    for dirpath, dirnames, filenames in os.walk(os.curdir):
        for filename in filenames:
            if filename.endswith('.py'):
                warnings += check_path(os.path.join(dirpath, filename))
    raise SystemExit(warnings > 0)

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

from runtests import run_tests

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

        run_tests(os.path.join(top_dir, 'src'))

