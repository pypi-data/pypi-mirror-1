#!/usr/bin/env python

# Copyright 2009 Antoine d'Otreppe de Bouvette
#
# This file is part of the Aspyct library. see http://www.aspyct.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from distutils.core import setup
import Aspyct

modules = ["Aspyct", "_Aspyct.__init__", "_Aspyct.common", "_Aspyct.smart"]

if sys.version_info[0] == 2:
    modules.append("_Aspyct.py2x")
else:
    modules.append("_Aspyct.py3x")

setup(name='Aspyct',
      version=Aspyct.VERSION.replace('.', '-').replace(' ', '_'),
      description='Python 2.x and 3.x aspect oriented programming (AOP) tools',
      author='Antoine d\'Otreppe de Bouvette',
      author_email='a.dotreppe@gmail.com',
      url='http://www.aspyct.org/',
      py_modules=modules,
      license='GNU/LGPL')
