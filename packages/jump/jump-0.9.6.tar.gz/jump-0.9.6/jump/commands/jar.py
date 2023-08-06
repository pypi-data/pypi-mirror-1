#!/usr/bin/env python
# encoding: utf-8
"""
jar.py

Created by Olli Wang (olliwang@ollix.com) on 2009-10-26.
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

import jump
from jump.commands.main import JumpCommand


class JumpJarCommand(JumpCommand):
    """Jump jar command.

    Make a standalone JAR file.
    """
    usage = "make a standalone JAR file"
    parser = jump.commands.OptionParser()
    required_options = ['main_entry_point']

    # Basic configuration
    onejar_jar_filename = os.path.join(jump.lib_dir,
                                       'one-jar-ant-task-0.96.jar')
    template_dir = os.path.join(jump.template_dir, 'jar')

    def copy_default_resources(self):
        """Copies default resources to `build/resource` directory."""
        # Generate default license file
        license_template = os.path.join(jump.template_dir, 'resources',
                                        'license.mako')
        license_filename = os.path.join(self.build_resc_dir, 'LICENSE')
        JumpCommand.create_template_file(self, license_template,
                                         license_filename)

    def create_template_files(self, options):
        """Creates template files for ant in `build/temp`."""
        # Template variables
        template_vars = {"onejar_jar_filename": self.onejar_jar_filename,
                         "lib_dir_exists": os.path.isdir(self.lib_dir),
                         "binlib_dir_exists": os.path.isdir(self.binlib_dir),
                         "base_dir": self.base_dir,
                         "lib_dir": self.lib_dir,
                         "binlib_dir": self.binlib_dir,
                         "build_lib_dir": self.build_lib_dir,
                         "build_class_dir": self.build_class_dir,
                         "build_temp_dir": self.build_temp_dir,
                         "build_resc_dir": self.build_resc_dir}
        options.update(template_vars)
        # build.xml
        build_xml_template = os.path.join(self.template_dir, 'build.xml.mako')
        JumpCommand.create_template_file(self, build_xml_template,
                                         self.build_xml_filename, options)

    def command(self, args, options):
        """Executes the command."""
        self.setup_main_entry_point(options)
        self.copy_jython_jars(options)
        self.copy_python_libs(options, self.build_class_dir)
        self.copy_default_resources()
        self.setup_dist_environments(options)
        self.create_template_files(options)
        os.system('ant -buildfile %s' % self.build_xml_filename)
