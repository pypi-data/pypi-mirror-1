#!/usr/bin/env python
#
# Quuxo Resolution. Lightweight HTTP WSGI request handling.
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

from setup.ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from setup.epydoc import EpydocCommand
from setup.pyunit import PyUnitCommand


setup(name="Achoo",
      version="1.0",
      description="A fluent interface for testing Python objects.",
      long_description="""\
Achoo is a fluent interface for testing Python objects. It makes
making assertions about objects (is this object equal to this other one?)
and function and method calls (does calling this function with these
arguments raise an error?) easy.
""",
      author="Quuxo Software",
      author_email="contact@quuxo.com",
      url="http://web.quuxo.com/projects/achoo",
      py_modules=('achoo',),
      cmdclass={'doc': EpydocCommand,
                'test': PyUnitCommand})

