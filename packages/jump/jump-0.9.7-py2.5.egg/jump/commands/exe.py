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

import oparse

from jump.commands.main import JumpCommand


class JumpExeCommand(JumpCommand):
    """Jump exe command.

    Make Windows native executables.
    """
    usage = "make Windows native executables"
    parser = oparse.OptionParser()
    parser.add_option('--gui', action="store_true", default=False,
                      help="use GUI instead of console mode")
    parser.add_option('--ico', action="store",
                      default='${jump.dir}/resources/jump.ico',
                      help="application icon in ICO format")
    parser.add_option('--onefile', action="store_true", default=False,
                      help="generate only one exe file")
    required_options = ['main_entry_point']

    def command(self, args, options):
        """Executes the command."""
        self.initialize(options)
        # Create build.xml
        self.create_template_file(self.build_xml_template,
                                  self.build_xml_filename)
        target = 'oneexe' if options.onefile else 'exe'
        os.system('ant %s -buildfile %s' % (target, self.build_xml_filename))
