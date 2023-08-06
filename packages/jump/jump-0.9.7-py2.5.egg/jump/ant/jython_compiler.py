#!/usr/bin/env python
# encoding: utf-8
"""
jython_compiler.py

Created by Olli Wang (olliwang@ollix.com) on 2009-11-18.
Copyright (c) 2009 Ollix. All rights reserved.

Jump is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or any later version.

Jump is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with Jump. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import shutil

from pylibtracer.libtracer import LibTracer

from com.ollix.jump.ant import JythonCompilerType


class JythonCompiler(JythonCompilerType):
    """Copies and compiles required Python modules to specified directory."""

    def __init__(self, dest_dir=None, packages=None):
        self.dest_dir = dest_dir
        self.packages = packages

    def execute(self):
        if self.packages:
            packages = self.packages.split(',')

        # Find all required Python modules or packages and copy them
        # to the specified destnation directory
        sys.path.append(self.dest_dir)
        lib_tracer = LibTracer('.', quiet=True, full_packages=self.packages)
        lib_locations = lib_tracer.get_lib_locations()
        for sys_path, relative_path in lib_locations:
            src_path = os.path.join(sys_path, relative_path)
            dest_path = os.path.join(self.dest_dir, relative_path)
            dest_dirname = os.path.dirname(dest_path)
            if not os.path.isdir(dest_dirname):
                os.makedirs(dest_dirname)
            shutil.copy2(src_path, dest_path)
        print 'Compiling %d source files to %s' % (len(lib_locations),
                                                   self.dest_dir)

    def setDestDir(self, dest_dir):
        self.dest_dir = dest_dir

    def setFullPackages(self, packages):
        self.packages = packages
