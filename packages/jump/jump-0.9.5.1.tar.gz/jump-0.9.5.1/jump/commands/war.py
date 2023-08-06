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

import jump
from jump.commands.main import JumpCommand


class JumpWarCommand(JumpCommand):
    """Jump war command.

    Make a War file for Python WSGI applications.
    """
    usage = "make a War file for Python WSGI applications"
    parser = jump.commands.OptionParser()
    parser.add_option('--wsgi_handler', action="store",
                      default='application.handler',
                      help="callable wsgi handler")
    parser.add_option('--log_level', action="store", default='debug',
                      help="the level of diagnostic output should be logged")
    parser.add_option('--cache_callables', action="store_true",
                      default=False,  help="whether or not it should cache " \
                                           "any callables it creates")
    parser.add_option('-g', '--google_app_engine', action="store",
                      default=None,  help="should set in the form of " \
                                          "`ID:VERSION`")
    parser.add_option('--no_multithread', action="store_true", default=False,
                      help="whether to run in multithread mode")
    required_options = ['wsgi_handler']

    # Basic configuration
    template_dir = os.path.join(jump.template_dir, 'war')

    def create_template_files(self, options):
        """Creates template files for ant in `build/temp`."""
        # Template variables
        if options.google_app_engine:
            try:
                gae_id, gae_version = options.google_app_engine.split(':')
            except ValueError:
                error_message = "`google_app_engine` parameter is not set " \
                                "properly."
                raise jump.commands.CommandError(error_message)
            else:
                options.gae_id, options.gae_version = gae_id, gae_version
                options.no_multithread = True

        web_xml_filename = os.path.join(JumpCommand.build_temp_dir, 'web.xml')
        appengine_xml_filename = 'appengine-web.xml'
        template_vars = {"web_xml_filename": web_xml_filename,
                         "appengine_xml_filename": appengine_xml_filename,
                         "lib_dir_exists": os.path.isdir(self.lib_dir),
                         "base_dir": self.base_dir,
                         "lib_dir": self.lib_dir,
                         "build_lib_dir": self.build_lib_dir,
                         "build_class_dir": self.build_class_dir,
                         "build_temp_dir": self.build_temp_dir}
        options.update(template_vars)
        # build.xml
        build_xml_template = os.path.join(self.template_dir, 'build.xml.mako')
        JumpCommand.create_template_file(self, build_xml_template,
                                         self.build_xml_filename, options)
        # web.xml
        web_xml_template = os.path.join(self.template_dir, 'web.xml.mako')
        JumpCommand.create_template_file(self, web_xml_template,
                                         web_xml_filename, options)
        # appengine-web.xml
        if options.google_app_engine:
            appengine_xml_template = os.path.join(self.template_dir,
                                                  'appengine-web.xml.mako')
            appengine_xml_filename = os.path.join(JumpCommand.build_temp_dir,
                                                  appengine_xml_filename)
            JumpCommand.create_template_file(self, appengine_xml_template,
                                             appengine_xml_filename, options)

    def command(self, args, options):
        """Executes the command."""
        self.copy_jython_jars(options)
        self.copy_python_libs(options, self.build_class_dir)
        self.setup_dist_environments(options)
        self.create_template_files(options)
        os.system('ant -buildfile %s' % self.build_xml_filename)
