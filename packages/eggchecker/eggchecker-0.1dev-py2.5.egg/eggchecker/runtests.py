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
extracted and adapted from zope testrunner script
"""
import logging
import os
import sys
import warnings

def run_tests(root_directory):
    """launch tests over zope.testrunner"""
    root_directory = os.path.abspath(root_directory)

    # removing root from parg
    sys.path[:] = [p for p in sys.path
                  if os.path.abspath(p) != root_directory]

    # add root to path
    if root_directory not in sys.path:
        sys.path.insert(0, root_directory)

    from zope.testing import testrunner
    defaults = ['--tests-pattern', '^f?tests$',
                '--test-path', root_directory]

    # Get rid of twisted.conch.ssh warning
    warnings.filterwarnings(
    'ignore', 'PyCrypto', RuntimeWarning, 'twisted[.]conch[.]ssh')

    # removing 'ztest' from args
    sys.argv.remove('ztest')

    result = testrunner.run(defaults)

    # Avoid spurious error during exit. Some thing is trying to log
    # something after the files used by the logger have been closed.
    logging.disable(999999999)

    sys.exit(result)

