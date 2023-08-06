#!/usr/bin/env python
# encoding: utf-8
"""
libtracer.py

Created by Olli Wang (olliwang@ollix.com) on 2009-10-23.
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
import types
import copy


class LibTracer(object):
    """Traces all required Python modules from a certain directory."""

    module_extensions = ['.py', '$py.class', '.pyc', '.so']
    ignored_module_paths = ['ez_setup', 'setup']
    ignored_module_attribute_names = ['__builtins__', '__doc__', '__name__']

    def __init__(self, basedir, module_extensions=None, quiet=False):
        """Initialize a ModuleTracer instance.

        Converts the specified `basedir` to absolute path and adds it to the
        `sys.path` variable.

        Args:
            basedir: The directory for searching.
            module_extensions: Accepted module extensions.
            quiet: If True, be quiet during collecting.

        Raises:
            OSError: Raised if the specified `basedir` is not a directory.
        """
        # Raise error if specified `basedir` is not a directory
        if not os.path.isdir(basedir):
            raise OSError("No such directory: %r" % basedir)

        # Convert `basedir` to absolute path
        if os.path.isabs(basedir):
            self.basedir = basedir
        else:
            self.basedir = os.path.abspath(basedir)

        # Create a list of system paths appending specified directory
        sys.path.insert(0, self.basedir)

        self.module_paths = []
        self.quiet = quiet

        if module_extensions:
            self.module_extensions = module_extensions

    def convert_filename_to_module_path(self, filename):
        """Returns the module path by specified filename.

        The specified filename should be an absolute path and end with
        accepted extensions (`self.module_extensions`).

        Args:
            filename: The filename to be converted to module path.

        Returns:
            A string of the converted module path such as `some.module`.

        Raises:
            OSError: Raised if specified filename is invalid.
        """
        # Remove extension name
        for extension in self.module_extensions:
            if filename.endswith(extension):
                filename = filename.rsplit(extension, 1)[0]
                break
        else:
            raise OSError("The filename extension must be one of " \
                                 "`.py`, `.pyc` or `$py.class`.")

        try:
            for sys_path in sys.path:
                if filename.startswith(sys_path):
                    # Remove system path directory
                    filename = filename.split(sys_path, 1)[1]
                    # Remove leading seprator
                    filename = filename.split(os.path.sep, 1)[1]
                    # Replace all seprators with a dot (.)
                    filename = filename.replace(os.path.sep, '.')
                    return filename
        except IndexError:
            pass

        raise OSError("Cound't find the module path for %r" % filename)

    def __find_modules_from_directory(self):
        """Finds all Python modules under specified directory.

        Returns:
            A list of tuples of found modules' package path and module path.
        """
        for root, dirnames, basenames in os.walk(self.basedir):
            for basename in basenames:
                # FIXME (olliwang): should support all accepted extensions
                if not basename.endswith('.py'):
                    continue

                # Retrieve module path
                filename = os.path.join(root, basename)
                module_path = self.convert_filename_to_module_path(filename)

                if not self.quiet:
                    print 'Found Python module: %s' % filename

                self.__find_modules_from_module_path(module_path)
        return self.module_paths

    def __find_modules_from_module_path(self, module_path):
        """Finds Python modules from a module path.

        Args:
            module_path: The module path used to find modules.

        Returns:
            A list of found modules.
        """
        # Return if specified `module_path` was already in `self.module_paths`
        # or in `self.ignored_module_paths`
        if not module_path or module_path in self.module_paths or \
           module_path in self.ignored_module_paths:
            return

        try:
            module = __import__(module_path)
        except ImportError:
            return
        else:
            self.module_paths.append(module_path)

        for attribute_name in dir(module):
            if attribute_name in self.ignored_module_attribute_names:
                continue
            attribute = getattr(module, attribute_name)

           # Find module path for each attribute
            if isinstance(attribute, types.ModuleType) and \
               hasattr(attribute, '__file__'):
                module_file = attribute.__file__
                module_path = self.convert_filename_to_module_path(module_file)
            elif hasattr(attribute, '__module__'):
                module_path = attribute.__module__
            else:
                continue

            # Find modules recursively
            self.__find_modules_from_module_path(module_path)

    def get_lib_locations(self):
        """Gets library locations with system path and its relative path.

        We use the term library here instead of module because we could also
        find required `.jar` files for Jython.

        Returns:
            A list of tuples in the form of (SYSTEM_PATH, RELATIVE_PATH).
        """
        module_paths = self.__find_modules_from_directory()
        lib_locations = []
        for module_path in module_paths:
            module = __import__(module_path)
            try:
                module_filename = module.__file__
            except AttributeError:
                continue

            # Ignore `.jar` files and None for `module_filename`
            # TODO (olliwang): Support adding `.jar` files automatically
            if not module_filename or module_filename.endswith('.jar'):
                continue

            # Separate module_filename to system path and the rest
            for sys_path in sys.path:
                if module_filename.startswith(sys_path):
                    prefix = sys_path + os.path.sep
                    module_filename = module_filename.split(prefix, 1)[1]
                    location = (sys_path, module_filename)
                    if location not in lib_locations:
                        lib_locations.append(location)
                    break
        return lib_locations
