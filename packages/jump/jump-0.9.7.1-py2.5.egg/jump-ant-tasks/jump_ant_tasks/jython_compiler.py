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
import tempfile
import zipfile

from com.ollix.jump.ant import JythonCompilerType
from jump_ant_tasks.libtracer import LibTracer


class JythonCompiler(JythonCompilerType):
    """Copies and compiles required Python modules to specified directory."""

    tempdir = os.path.join(tempfile.gettempdir(), 'jump-eggs')

    def __init__(self, dest_dir=None, packages=None):
        self.dest_dir = dest_dir
        self.packages = packages

        self.updateSysPath()

    def updateSysPath(self):
        # Clean tempdir
        if os.path.isdir(self.tempdir):
            shutil.rmtree(self.tempdir)
        os.makedirs(self.tempdir)

        jython_lib_dir = os.path.join(os.environ['JYTHON_HOME'], 'Lib')
        site_package_dir = os.path.join(jython_lib_dir, 'site-packages')
        easy_install_pth = os.path.join(site_package_dir, 'easy-install.pth')
        sys.path.insert(0, jython_lib_dir)
        sys.path.insert(0, site_package_dir)
        if os.path.isfile(easy_install_pth):
            for line in open(easy_install_pth, 'r'):
                line = line.strip()
                if not line or ' ' in line:
                    continue
                if line.startswith('./'):
                    egg_path = os.path.join(site_package_dir, line[2:])
                elif line.startswith('/'):
                    egg_path = line
                else:
                    continue
                # Unpack zipped egg file
                if zipfile.is_zipfile(egg_path):
                    egg_path = self.unpack_egg(egg_path)
                sys.path.insert(0, egg_path)

    def unpack_egg(self, egg_path):
        egg = zipfile.ZipFile(egg_path)
        egg_name = os.path.basename(egg_path)
        egg_dir = os.path.join(self.tempdir, egg_name)

        for name in egg.namelist():
            target = os.path.join(egg_dir, name)
            target_dirname = os.path.dirname(target)
            if not os.path.isdir(target_dirname):
                os.makedirs(target_dirname)
            f = open(target, 'wb')
            try:
                f.write(egg.read(name))
            finally:
                f.close()
        return egg_dir

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
