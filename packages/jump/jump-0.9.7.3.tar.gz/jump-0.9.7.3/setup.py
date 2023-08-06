#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Olli Wang (olliwang@ollix.com) on 2009-10-20.
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

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


if not sys.platform.startswith('java'):
    print 'error: Jump can only be installed with Jython.'
    sys.exit()

setup(name='jump',
      version='0.9.7.3',
      description='Jump is a build tool for distributing Java and Jython ' \
                  'applications in a really simple step.',
      license="GPLv3",
      author='Olli Wang',
      author_email='olliwang@ollix.com',
      url='http://opensource.ollix.com/jump',
      packages=find_packages(exclude=['jump-jython-factory',
                                      'jump-jython-factory.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['oparse>=0.9.2',
                        'pylibtracer>=0.9.1',
                        'mako>=0.2.5'],
      extras_require = {},
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      jump = jump.commands.main:jump_command

      [jump.commands]
      jar = jump.commands.jar:JumpJarCommand
      jarlib = jump.commands.jarlib:JumpJarLibCommand
      exe = jump.commands.exe:JumpExeCommand
      app = jump.commands.app:JumpAppCommand
      war = jump.commands.war:JumpWarCommand
      ant = jump.commands.ant:JumpAntCommand
      """,
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Build Tools',
      ],
)
