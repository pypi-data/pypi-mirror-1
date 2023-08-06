#!/usr/bin/env python
# encoding: utf-8
"""
app.py

Created by Olli Wang (olliwang@ollix.com) on 2009-10-27.
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


class JumpAppCommand(JumpCommand):
    """Jump jar command.

    Make a Mac app bundle.
    """
    usage = "make a Mac app bundle"
    parser = jump.commands.OptionParser()
    parser.add_option('--vm_arguments', action="store", default="",
                      help="extra command-line arguments for the Java " \
                           "application")
    parser.add_option('--development_region', action="store",
                      default="English", help="the development region of " \
                                              "the bundle")
    parser.add_option('--icns', action="store", default=None,
                      help="file reference to a Mac OS X icon file")
    parser.add_option('--info_string', action="store", default="",
                      help="a string for display in the Finder's Get Info " \
                           "panel")
    parser.add_option('--jvm_version', action="store", default="1.5+",
                      help="the version of the JVM required to run the " \
                           "application")
    parser.add_option("--short_name", action="store", default="",
                      help="the string used in the application menu")
    parser.add_option("--signature", action="store", default="????",
                      help="the four-letter code identifying the bundle")
    parser.add_option("--vm_options", action="store", default="",
                      help="command line options to pass the JVM at startup")
    required_options = ['main_entry_point']

    # Basic configuration
    jarbundler_filename = os.path.join(jump.lib_dir, 'jarbundler-2.1.0.jar')
    template_dir = os.path.join(jump.template_dir, 'app')

    def create_template_files(self, options):
        """Creates template files for ant in `build/temp`."""
        # Template variables
        if options.icns:
            options.icns = os.path.abspath(options.icns)

        options.start_on_main_thread = 'false'
        if options.vm_options and \
           '-XstartOnFirstThread' in options.vm_options.split(" "):
                options.start_on_main_thread = 'true'

        template_vars = {"jarbundler_filename": self.jarbundler_filename,
                         "lib_dir_exists": os.path.isdir(self.lib_dir),
                         "base_dir": self.base_dir,
                         "lib_dir": self.lib_dir,
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
        self.setup_dist_environments(options)
        self.create_template_files(options)
        os.system('ant -buildfile %s' % self.build_xml_filename)
