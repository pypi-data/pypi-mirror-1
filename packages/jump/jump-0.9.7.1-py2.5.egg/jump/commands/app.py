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

import oparse

from jump.commands.main import JumpCommand


class JumpAppCommand(JumpCommand):
    """Jump app command.

    Make Mac Application Bundles.
    """
    usage = "make Mac Application Bundles"
    parser = oparse.OptionParser()
    parser.add_option('--vm_arguments', action="store", default="",
                      help="extra command-line arguments for the Java " \
                           "application")
    parser.add_option('--development_region', action="store",
                      default="English", help="the development region of " \
                                              "the bundle")
    parser.add_option('--icns', action="store",
                      default="${jump.dir}/resources/jump.icns",
                      help="file reference to a Mac OS X icon file")
    parser.add_option('--info_string', action="store", default="",
                      help="a string for display in the Finder's Get Info " \
                           "panel")
    parser.add_option('--jvm_version', action="store", default="1.5+",
                      help="the version of the JVM required to run the " \
                           "application")
    parser.add_option("--short_name", action="store",
                      default=JumpCommand.default_dist_name,
                      help="the string used in the application menu")
    parser.add_option("--signature", action="store", default="????",
                      help="the four-letter code identifying the bundle")
    parser.add_option("--vm_options", action="store", default="",
                      help="command line options to pass the JVM at startup")
    required_options = ['main_entry_point']

    def command(self, args, options):
        """Executes the command."""
        self.initialize(options)
        # Create build.xml
        self.create_template_file(self.build_xml_template,
                                  self.build_xml_filename)
        os.system('ant app -buildfile %s' % self.build_xml_filename)
