#!/usr/bin/env python
# encoding: utf-8
"""
jython_driver.py

Created by Olli Wang (olliwang@ollix.com) on 2009-11-18.
Copyright (c) 2009 Ollix. All rights reserved.
"""

import os
import sys

from com.ollix.jump.ant import JythonDriverType


jython_lib_dir = os.path.join(os.environ['JYTHON_HOME'], 'Lib')
site_package_dir = os.path.join(jython_lib_dir, 'site-packages')
easy_install_pth = os.path.join(site_package_dir, 'easy-install.pth')
if os.path.isfile(easy_install_pth):
    for line in open(easy_install_pth, 'r'):
        line = line.strip()
        if line and ' ' not in line:
            if line.startswith('./'):
                path = os.path.join(site_package_dir, line[2:])
            elif line.startswith('/'):
                path = line
            else:
                continue
            sys.path.insert(0, path)

from mako.template import Template

import jump


class JythonDriver(JythonDriverType):

    def __init__(self, dest_dir=None, main_entry_point=None):
        self.dest_dir = dest_dir
        self.main_entry_point = main_entry_point

    def execute(self):
        try:
            py_module, py_func = self.main_entry_point.split(':')
        except ValueError:
            # Set Java main class
            return

        # Use default Main.java file to trigger Python main entry point
        template_vars = {'py_main_module': py_module, 'py_main_func': py_func}
        filename = 'Main.java'
        output_filename = os.path.join(self.dest_dir, filename)
        build_tempalte = Template(filename=os.path.join(jump.temp_dir,
                                                        filename))
        dest_file = open(output_filename, 'w')
        dest_file.write(build_tempalte.render(**dict(py_main_module=py_module,
                                                     py_main_func=py_func)))
        dest_file.close()
        print "Create file: %s" % output_filename

    def setDestDir(self, dest_dir):
        self.dest_dir = dest_dir

    def setMainEntryPoint(self, main_entry_point):
        self.main_entry_point = main_entry_point
