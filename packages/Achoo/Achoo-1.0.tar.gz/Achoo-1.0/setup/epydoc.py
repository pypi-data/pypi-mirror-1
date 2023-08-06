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
from distutils.errors import *

import os
import subprocess


class EpydocCommand(Command):
    """
    A command for generating docoumentation using Epydoc.
    """

    description = 'Generates API documentation using Epydoc'

    user_options = []

    def initialize_options(self):
        self.config = None
        self.target = None
        self.output = None
        self.name = self.distribution.name
        self.url = self.distribution.url
        self.verbose = True
        self.objects = None

    def finalize_options(self):
        if not self.objects:
            # XXX is this the right thing to do?
            self.objects = []
            if self.distribution.py_modules:
                # we want epydoc running on the module files themselves,
                # rather than any version already installed on the
                # system, so try to kluge around the lack of a list of them
                self.objects += ['%s.py' % mod
                                 for mod in self.distribution.py_modules]
            if self.distribution.packages:
                self.objects += list(self.distribution.packages)

    def run(self):
        # XXX run it as a subprocess, it's easier to invoke than using
        # the epydoc API :(
        cmd = ['epydoc']
        if self.target:
            cmd += ['--' + self.target]
        if self.config:
            cmd += ['--config', self.config]
        if self.output:
            self.mkpath(self.output)
            cmd += ['--output', self.output]
        if self.name:
            cmd += ['--name', self.name]
        if self.url:
            cmd += ['--url', self.url]
        if self.verbose:
            cmd += ['--verbose']
        if self.objects:
            cmd += self.objects

        self.spawn(cmd)
