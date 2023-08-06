#!/usr/bin/env python
# encoding: utf-8
"""
exe.py

Created by Olli Wang (olliwang@ollix.com) on 2009-10-28.
Copyright (c) 2009 Ollix. All rights reserved.

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


class JumpExeCommand(JumpCommand):
    """Jump exe command.

    Make Windows native executables.
    """
    usage = "make Windows native executables"
    parser = jump.commands.OptionParser()
    parser.add_option('--gui', action="store_true", default=False,
                      help="use GUI instead of console mode")
    parser.add_option('--ico', action="store", default=None,
                      help="application icon in ICO format")

    # Basic configuration
    template_dir = os.path.join(jump.template_dir, 'exe')
    launch4j_dir = os.path.join(jump.lib_dir, 'launch4j')
    launch4j_filename = os.path.join(launch4j_dir, 'launch4j.jar')
    xstream_filename = os.path.join(launch4j_dir, 'xstream.jar')
    launch4j_xml_filename = os.path.join(JumpCommand.build_temp_dir,
                                         'launch4j.xml')
    required_options = ['main_entry_point']

    def create_template_files(self, options):
        """Creates template files for ant in `build/temp`."""
        # Template variables
        if options.ico:
            options.ico = os.path.abspath(options.ico)
        # Find class paths
        classpaths = []
        for lib_dir in (self.lib_dir, self.build_lib_dir):
            lib_dir += os.path.sep
            for root, dirnames, basenames in os.walk(lib_dir):
                for basename in basenames:
                    if not basename.endswith('.jar'):
                        continue
                    abs_classpath = os.path.join(root, basename)
                    rel_classpath = abs_classpath.split(lib_dir)[1]
                    classpath = os.path.join('lib', rel_classpath)
                    classpaths.append(classpath)
        template_vars = {"lib_dir_exists": os.path.isdir(self.lib_dir),
                         "base_dir": self.base_dir,
                         "lib_dir": self.lib_dir,
                         "build_lib_dir": self.build_lib_dir,
                         "build_class_dir": self.build_class_dir,
                         "build_temp_dir": self.build_temp_dir,
                         "launch4j_dir": self.launch4j_dir,
                         "launch4j_filename": self.launch4j_filename,
                         "xstream_filename": self.xstream_filename,
                         "launch4j_xml_filename": self.launch4j_xml_filename,
                         "classpaths": classpaths}
        options.update(template_vars)
        # build.xml
        build_xml_template = os.path.join(self.template_dir, 'build.xml.mako')
        JumpCommand.create_template_file(self, build_xml_template,
                                         self.build_xml_filename, options)
        # launch4j.xml
        if not os.path.isfile(self.launch4j_xml_filename):
            launch4j_xml_template = os.path.join(self.template_dir,
                                                 'launch4j.xml.mako')
            JumpCommand.create_template_file(self, launch4j_xml_template,
                                             self.launch4j_xml_filename,
                                             options)

    def command(self, args, options):
        """Executes the command."""
        self.setup_main_entry_point(options)
        self.copy_jython_jars(options)
        self.copy_python_libs(options, self.build_class_dir)
        self.setup_dist_environments(options)
        self.create_template_files(options)
        os.system('ant -buildfile %s' % self.build_xml_filename)
