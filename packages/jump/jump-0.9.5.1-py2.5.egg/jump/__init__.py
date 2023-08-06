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


VERSION = "0.9.5.1"

# Directory paths
lib_dir = pkg_resources.resource_filename('jump', 'lib')
template_dir = pkg_resources.resource_filename('jump', 'templates')
