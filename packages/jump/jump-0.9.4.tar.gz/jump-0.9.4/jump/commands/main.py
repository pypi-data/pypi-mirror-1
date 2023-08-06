#!/usr/bin/env python
# encoding: utf-8
"""
jump.py

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
import sys
import shutil

import jump


class JumpCommand(jump.commands.Command):
    """The basic Jump command.

    This class implement the basic Jump command. All Jump's subcommand classes
    should inherit from this class.

    Attributes:
        subcmd_entry_point: The entry point name for Jump's subcommands.
        usage: Modifies the default usage by adding a command argument.
        version: Indicates the current Jump version.
        parser: Instantiates OptionParse class to add some parser options.
    """
    subcmd_entry_point = 'jump.commands'
    usage = '%prog command [options] arg1 arg2 ...'
    version = '%prog ' + jump.VERSION
    config_filename = 'config.jp'

    # Basic configuration
    base_dir = os.getcwd()
    lib_dir = os.path.join(base_dir, 'lib')
    build_dir = os.path.join(base_dir, 'build')
    build_lib_dir = os.path.join(build_dir, 'lib')
    build_class_dir = os.path.join(build_dir, 'classes')
    build_resc_dir = os.path.join(build_dir, 'resources')
    build_temp_dir = os.path.join(build_dir, 'temp')

    config_filename = os.path.join(base_dir, config_filename)
    build_xml_filename = os.path.join(build_temp_dir, 'build.xml')
    default_main_java_filename = os.path.join(build_temp_dir, 'Main.java')
    license_filename = os.path.join(build_resc_dir, 'LICENSE')

    # Command options
    parser = jump.commands.OptionParser()
    parser.add_option('-v', '--verbose', action="store_true",
                      default=False, help="run in verbose mode")
    parser.add_option('-n', '--dist_name', action="store",
                      default=os.path.basename(base_dir),
                      help="name of the distribution file")
    parser.add_option('-p', '--include_packages', action="store",
                      default=None, help="include full Python packages")
    parser.add_option('-d', '--dist_dir', action="store",
                      default=os.path.join(base_dir, 'dist'),
                      help="directory to put the distribution")

    def __init__(self):
        """Initialize build environments.

        Creates some directories for build, the created directories include:
            CURRENT_DIRECTORY
            |-- build           # build-related files
                |-- lib         # .jar files
                |-- classes     # Java bytecode class files
                |-- resources   # static files
                |-- temp        # temporary files
        """
        # Create `build` and nested directories
        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.mkdir(self.build_dir)
        for dir_name in (self.build_lib_dir, self.build_class_dir,
                         self.build_resc_dir, self.build_temp_dir):
            os.mkdir(dir_name)

    def setup_dist_environments(self, options):
        """Setup distribuiton enviroments"""
        # Convert dist_dir to absolute path
        if not os.path.isabs(options.dist_dir):
            options.dist_dir = os.path.abspath(options.dist_dir)

        if not os.path.isdir(options.dist_dir):
            try:
                os.mkdir(options.dist_dir)
            except OSError:
                parent_dir = os.path.dirname(options.dist_dir)
                error_message = "Could not make the `dist_dir` directory " \
                                "because %r does not exist." % (parent_dir,)
                raise jump.commands.CommandError(error_message)
        options.dist_path = os.path.join(options.dist_dir, options.dist_name)

    def copy_jython_jars(self, options):
        """Copies required `.jar` files to `build/lib` directory."""
        java_class_paths = sys.registry['java.class.path'].split(':')
        for path in java_class_paths:
            jython_dirname, jython_jar_filename = os.path.split(path)
            if jython_jar_filename != 'jython.jar':
                continue

            jythonlib_jar_filename = os.path.join(jython_dirname,
                                                  'jython-lib.jar')
            if not os.path.isfile(jythonlib_jar_filename):
                options.jythonlib_not_exist = True
            else:
                options.jythonlib_not_exist = False

            options.jython_dirname = jython_dirname
            options.jythonlib_dirname = os.path.join(jython_dirname, 'Lib')
            options.jythonlib_jar_filename = jythonlib_jar_filename
            break
        else:
            error_message = "Jump could not find your `jython.jar`, please " \
                            "make sure this file is added to your class path."
            raise jump.commands.CommandError(error_message)

    def copy_python_libs(self, options, dest_dir):
        """Copies required Python modules to specified directory."""
        if options.include_packages:
            full_packages = options.include_packages.split(',')
        else:
            full_packages = None

        # Find all required Python modules or packages and copy them
        # to the specified destnation directory
        lib_tracer = jump.libtracer.LibTracer(self.base_dir, quiet=False,
                                              full_packages=full_packages)
        lib_locations = lib_tracer.get_lib_locations()
        for sys_path, relative_path in lib_locations:
            src_path = os.path.join(sys_path, relative_path)
            dest_path = os.path.join(dest_dir, relative_path)
            dest_dirname = os.path.dirname(dest_path)
            if not os.path.isdir(dest_dirname):
                os.makedirs(dest_dirname)
            shutil.copy2(src_path, dest_path)

    def command(self, args, options):
        """Returns help message."""
        JumpCommand().run('-h')

    def clean(self):
        """Removes all generated files used for build."""
        # Remove `build` directory
        shutil.rmtree(self.build_dir)

def jump_command():
    """Runs the Jump command."""
    JumpCommand().run()
