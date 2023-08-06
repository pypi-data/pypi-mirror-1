#
# Achoo. A fluent interface for testing Python objects.
# Copyright (C) 2008 Quuxo Software.
# <http://web.quuxo.com/projects/achoo>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#

from distutils.core import Command

import os
import subprocess
import sys
import unittest


class PyUnitCommand(Command):
    """
    A command for running PyUnit unit tests.
    """

    description = 'Executes PyUnit tests'

    user_options = [('test=', 't',
                     'Name of unit test filename or module[.class[.method]]')]


    def initialize_options(self):
        self.test_dir = 'test'
        self.test = None

    def finalize_options(self):
        pass

    def run(self):
        tests = []

        def load_test(name):
            if _is_py(name):
                name = os.path.splitext(name)[0]
            elif name.startswith(self.test_dir):
                name = name[len(self.test_dir) + 1:]
            elif os.sep in name:
                name = name.replace(os.sep, '.')
            suite = unittest.defaultTestLoader.loadTestsFromName(name)
            tests.append(suite)

        if self.test:
            load_test(self.test)
        else:
            for dir, dir_names, file_names in os.walk(self.test_dir):
                for file_name in file_names:
                    if _is_py(file_name):
                        load_test(os.path.join(dir, file_name))

        test_runner = unittest.TextTestRunner(verbosity=2)
        for test in tests:
            test_runner.run(test)


def _is_py(filename):
    return os.path.splitext(filename)[1] == '.py'
