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

import oparse

from jump.commands.main import JumpCommand


class JumpJarCommand(JumpCommand):
    """Jump jar command.

    Make standalone JAR files.
    """
    usage = "make standalone JAR files"
    parser = oparse.OptionParser()
    required_options = ['main_entry_point']

    def command(self, args, options):
        """Executes the command."""
        self.initialize(options)
        # Create build.xml
        self.create_template_file(self.build_xml_template,
                                  self.build_xml_filename)
        os.system('ant jar -buildfile %s' % self.build_xml_filename)
