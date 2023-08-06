#!/usr/bin/env python
# encoding: utf-8
"""
jarlib.py

Created by Olli Wang (olliwang@ollix.com) on 2009-10-27.
Copyright (c) 2009 Ollix. All rights reserved.

This file is part of Jump.

Jump is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or any later version.

Jump is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with Jump.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys

import jump
from jump.commands.main import JumpCommand


class JumpJarLibCommand(JumpCommand):
    """Jump jarlib command.

    Make a JAR library file.
    """
    usage = "make a JAR library file"
    parser = jump.commands.OptionParser()

    # Basic configuration
    template_dir = os.path.join(jump.template_dir, 'jarlib')

    def create_template_files(self, options):
        """Creates template files for ant in `build/temp`."""
        # Template variables
        classpaths = sys.registry['java.class.path'].split(':')
        template_vars = {"classpaths": classpaths,
                         "lib_dir_exists": os.path.isdir(self.lib_dir),
                         "base_dir": self.base_dir,
                         "lib_dir": self.lib_dir,
                         "build_lib_dir": self.build_lib_dir,
                         "build_class_dir": self.build_class_dir}
        options.update(template_vars)
        # build.xml
        build_xml_template = os.path.join(self.template_dir, 'build.xml.mako')
        JumpCommand.create_template_file(self, build_xml_template,
                                         self.build_xml_filename, options)

    def command(self, args, options):
        """Executes the command."""
        self.copy_python_libs(options, self.build_class_dir)
        self.setup_dist_environments(options)
        self.create_template_files(options)
        os.system('ant -buildfile %s' % self.build_xml_filename)
