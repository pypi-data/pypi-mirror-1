#!/usr/bin/env python
# encoding: utf-8
"""
commands.py

Created by Olli Wang (olliwang@ollix.com) on 2009-10-21.
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

import pkg_resources

from jump import commands
from jump import libtracer


VERSION = "0.9.4"
lib_dir = pkg_resources.resource_filename('jump', 'lib')
template_dir = pkg_resources.resource_filename('jump', 'templates')

# Resource paths
jython_jar_filename = os.path.join(lib_dir, 'jython.jar')
jythonlib_jar_filename = os.path.join(lib_dir, 'jython-lib.jar')
onejar_jar_filename = os.path.join(lib_dir, 'one-jar-ant-task-0.96.jar')

# Template paths
build_xml_template = os.path.join(template_dir, 'build.xml.mako')
main_java_template = os.path.join(template_dir, 'main.java.mako')
license_template = os.path.join(template_dir, 'license.mako')
