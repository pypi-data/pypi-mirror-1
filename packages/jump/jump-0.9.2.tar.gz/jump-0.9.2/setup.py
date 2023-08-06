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

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import jump


setup(name='jump',
      version=jump.VERSION,
      description='Distributing Jython Scripts in a Jump!',
      license="GPLv3",
      author='Olli Wang',
      author_email='olliwang@ollix.com',
      url='http://gitorious.org/jump',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['mako>=0.2.5'],
      extras_require = {},
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      jump = jump.commands:jump_command

      [jump.commands]
      dist = jump.commands:JumpDistCommand
      """,
      classifiers=[
          'Intended Audience :: Developers',
          "License :: OSI Approved",
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Build Tools',
      ],
)
