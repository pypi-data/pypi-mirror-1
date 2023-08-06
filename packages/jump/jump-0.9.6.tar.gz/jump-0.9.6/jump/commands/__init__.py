#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

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
import optparse

import pkg_resources


class CommandError(Exception):
    pass

class OptionParser(object):
    """Simulates optparse.OptionParser for adding options in command classes.

    This class should only be used by classes which inherit from Command
    class. These command classes then can add options by instantiating this
    class as a class variable named `parser`, and use it to add group options
    as using optparse.OptionParser.

    For example:
    class SomeCommand(Command):
        parser = OptionParser()
        parser.add_option("-v", "--verbose", action="store_true",
                          default=False, help="run in verbose mode")
    """
    def __init__(self):
        self.__options = []

    def add_option(self, *args, **kw):
        self.__options.append((args, kw))

    def add_options_to_parser(self, parser):
        for args, kw in self.__options:
            parser.add_option(*args, **kw)

    def has_options(self):
        if self.__options:
            return True
        else:
            return False

class CommandOption(dict):
    """A wrapper for optparse.parser parsed options

    Adds the dictionary ability to the parsed options.
    """
    def __init__(self, options):
        for option_name in dir(options):
            if not option_name.startswith('_') and \
               option_name not in ('ensure_value', 'read_file',
                                   'read_module'):
                self[option_name] = getattr(options, option_name)

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

class Command(object):
    """The base class for commands.

    This is the base class for all commands. To implement a real command, you
    need to create a class inheriting from this base class and define a
    `command` method to do the real work. Note that you need to add two
    additional parameters to the `command` method in order to receive
    arguments and options received from command line. You also need to
    instantiate a OptionParser instance as a class variable for adding some
    group options and a usage variable explaining what this command does.

    For example:
    class SomeCommand(Command):
        usage = 'I can do something'

        parser = OptionParser()     # This line is required
        parser.add_option("-v", "--verbose", action="store_true",
                          default=False, help="run in verbose mode")

        def command(self, args, options):
            print "Hi, I'm a sub-command!"
            print "Received args:", args
            print "Received options:", options

    Attributes:
        usage: The usage message displayed in help message.
        description: description displayed in the help message.
        version: The string to print when supplying --version option.
        config_filename: A string of used config filename.
        required_options: A list of required command options.
    """

    usage = '%prog [options] arg1 arg2 ...'
    description = None
    version = None
    config_filename = None
    required_options = None

    def __call__(self, *args):
        """Executes the command.

        This method is only a delegate to the `__run` method but also catches
        all CommandErrors and displays the error message.
        """
        try:
            self.__run(*args)
        except CommandError, e:
            print 'Error:', e.message

    def generate_usage(self):
        """Generates usage messages for parser."""
        usage = [self.usage]
        # Add description
        if self.description:
            usage.append('\n' + self.description)
        # Add subcommand usages if available
        if hasattr(self, 'subcmd_entry_point'):
            usage.append("\nCommands:")
            subcmd_entry_point = self.subcmd_entry_point
            for command in pkg_resources.iter_entry_points(subcmd_entry_point):
                command_class = command.load()
                usage.append('  %s: %s' % (command.name, command_class.usage))
        return '\n'.join(usage)

    def adopt_config_parameters(self, args):
        """Adopts config parameters into command options."""
        if not self.config_filename or \
           not os.path.isfile(self.config_filename):
            return

        config_file = open(self.config_filename, 'r')
        arg_index = 0
        for line in config_file:
            # Ignore from `#` to the end of line
            line = line.split('#')[0].strip()
            if not line:
                continue
            # Add parameters to `self.config` variable
            try:
                key, value = line.split('=')
            except ValueError:
                if ' ' not in line:
                    option = '--%s' % line
                else:
                    raise CommandError("Syntax error in config file: %r" % \
                                       line)
            else:
                option = '--%s=%s' % (key.strip(), value.strip())
            args.insert(arg_index, option)
            arg_index += 1
        config_file.close()

    def check_required_options(self, options):
        """Check required options.

        Raises:
            CommandError: Raised if required options are not specified.
        """
        if not self.required_options:
            return

        for option_name in self.required_options:
            if not getattr(options, option_name):
                raise CommandError("%r parameter is required." % option_name)

    def __run(self, *args):
        """Executes the command.

        Decides which command to run and execute the `command` method
        within the proper command class. It also passes two arguments,
        `args` and `options`, parsed by optparse.OptionParser to the
        `command` method. You can also pass arguments directly to this method
        instead of calling it from command line.
        """
        # Set arguements from command line if not specified in parameters
        if args:
            args = list(args)
        else:
            args = sys.argv[1:]
        self.adopt_config_parameters(args)

        parser = optparse.OptionParser(usage=self.generate_usage(),
                                       version=self.version)
        # Add options to parser
        if hasattr(self, 'parser') and isinstance(self.parser, OptionParser):
            self.parser.add_options_to_parser(parser)

        # Create a variable to cache subcommand classes in the form of
        # {COMMAND_NAME: COMMAND_CLASS, ...}
        command_classes = {}

        # Include subcommands if defined subcmd_entry_point
        if hasattr(self, 'subcmd_entry_point'):
            # Find all subcommand classes and add group options if available
            subcmd_entry_point = self.subcmd_entry_point
            for command in pkg_resources.iter_entry_points(subcmd_entry_point):
                command_class = command.load()

                # Add group options if specified
                if hasattr(command_class, 'parser') and \
                   isinstance(command_class.parser, OptionParser) and \
                   command_class.parser.has_options():
                    option_group = optparse.OptionGroup(parser, command.name)
                    command_class.parser.add_options_to_parser(option_group)
                    parser.add_option_group(option_group)

                # Cache command class
                command_classes[command.name] = command_class

        # Parse arguments from command line
        (options, args) = parser.parse_args(list(args))
        options = CommandOption(options)
        # Determine the command instance
        command_name = args[0] if args else None
        if command_name in command_classes:
            args.pop(0)     # Remove the subcommand argument
            command_class = command_classes[command_name]
            command_instance = command_class()
        else:
            command_instance = self
        # Check required parameters
        command_instance.check_required_options(options)
        # Execute the command
        command_instance.command(args, options)
        # Execute clean function
        command_instance.clean()

    def command(self, args, options):
        """The real place to execute the command.

        This method should be implemented manually in subclasses in order to
        execute the command.
        """
        raise NotImplementedError()

    def clean(self):
        """Executed after each command terminated.

        This method should be implemented manually in subclasses.
        """
        pass
