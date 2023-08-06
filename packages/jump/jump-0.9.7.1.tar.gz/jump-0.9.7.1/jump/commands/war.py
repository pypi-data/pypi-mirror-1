#!/usr/bin/env python
# encoding: utf-8
"""
war.py

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


class JumpWarCommand(JumpCommand):
    """Jump war command.

    Make a War file for Python WSGI applications.
    """
    usage = "make a War file for Python WSGI applications"
    parser = oparse.OptionParser()
    parser.add_option('--wsgi_handler', action="store",
                      default='application.handler',
                      help="callable wsgi handler")
    parser.add_option('--log_level', action="store", default='debug',
                      help="the level of diagnostic output should be logged")
    parser.add_option('--cache_callables', action="store_true",
                      default=False,  help="whether or not it should cache " \
                                           "any callables it creates")
    parser.add_option('-g', '--google_app_engine', action="store",
                      default="",  help="should set in the form of " \
                                          "`ID:VERSION`")
    parser.add_option('--no_multithread', action="store_true", default=False,
                      help="whether to run in multithread mode")

    def command(self, args, options):
        """Executes the command."""
        self.initialize(options)
        # Create build.xml
        self.create_template_file(self.build_xml_template,
                                  self.build_xml_filename)
        os.system('ant war -buildfile %s' % self.build_xml_filename)
