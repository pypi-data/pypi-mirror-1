#!/usr/bin/env python
# encoding: utf-8
"""
command.py

Created by Olli Wang (olliwang@ollix.com) on 2009-11-17.
Copyright (c) 2009 Ollix. All rights reserved.
"""

import os
import sys
import optparse
import ConfigParser

import pkg_resources

import oparse


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
        config: The ConfigParser object read specified config file.
        config_filename: A string of used config filename.
        config_option_section: The section name used to set command options.
        required_options: A list of required command options.
        subcommand_entry_point: The entry point of subcommands.
    """

    usage = '%prog [options] arg1 arg2 ...'
    description = None
    version = None
    config = ConfigParser.ConfigParser()
    config_filename = None
    config_option_section = 'options'
    required_options = None
    subcommand_entry_point = None

    def __call__(self, *args):
        """Executes the command.

        This method is only a delegate to the `__run` method but also catches
        all CommandErrors and displays the error message.
        """
        try:
            self.__run(*args)
        except oparse.CommandError, e:
            print 'Error:', e.message

    def generate_usage(self, subcommand_instances):
        """Generates usage messages for parser."""
        usage = [self.usage]
        # Add description
        if self.description:
            usage.append('\n' + self.description)
        # Add usages of subcommands if available
        if subcommand_instances:
            usage.append("\nCommands:")
            for command_name, command_inst in subcommand_instances.items():
                usage.append('  %s: %s' % (command_name, command_inst.usage))
        return '\n'.join(usage)

    def adopt_config_parameters(self, args):
        """Adopts config parameters into command options."""
        if not self.config_filename or \
           not os.path.isfile(self.config_filename):
            return

        self.config.read(self.config_filename)
        # Returns if not found the option section
        if not self.config.has_section(self.config_option_section):
            return

        arg_index = 0
        section_name = self.config_option_section
        for option_name, option_value in self.config.items(section_name):
            if option_value:
                option = '--%s=%s' % (option_name, option_value)
            else:
                option = '--%s' % option_name
            args.insert(arg_index, option)
            arg_index += 1

    def __check_required_options(self, options):
        """Check required options.

        Raises:
            CommandError: Raised if required options are not specified.
        """
        if not self.required_options:
            return

        for option_name in self.required_options:
            if not getattr(options, option_name):
                error_msg = "%r parameter is required." % option_name
                raise oparse.CommandError(error_msg)

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

        # Create a variable to cache subcommand instances in the form of
        # {COMMAND_NAME: COMMAND_INSTANCE, ...}
        subcommand_instances = {}
        # Include subcommands if subcmd_entry_point defined
        if self.subcommand_entry_point:
            # Find all subcommand classes and add group options if available
            entry_point = self.subcommand_entry_point
            for command in pkg_resources.iter_entry_points(entry_point):
                command_callable = command.load()
                if repr(command_callable).startswith('<class'):
                    command_instance = command_callable()
                else:
                    command_instance = command_callable
                subcommand_instances[command.name] = command_instance

        usage = self.generate_usage(subcommand_instances)
        parser = optparse.OptionParser(usage=usage, version=self.version)
        # Add options to parser
        if hasattr(self, 'parser') and isinstance(self.parser,
                                                  oparse.OptionParser):
            self.parser.add_options_to_parser(parser)
            # Add subcommands' options
            for command_name, command_inst in subcommand_instances.items():
                # Add group options if specified
                if hasattr(command_inst, 'parser') and \
                   isinstance(command_inst.parser, oparse.OptionParser) and \
                   command_inst.parser.has_options():
                    option_group = optparse.OptionGroup(parser, command_name)
                    command_inst.parser.add_options_to_parser(option_group)
                    parser.add_option_group(option_group)

        # Parse arguments from command line
        (options, args) = parser.parse_args(list(args))
        options = CommandOption(options)
        # Determine the command instance
        command_name = args[0] if args else None
        if command_name in subcommand_instances:
            args.pop(0)     # Remove the subcommand argument
            command_instance = subcommand_instances[command_name]
        else:
            command_instance = self
        # Set config instance
        command_instance.config = self.config
        # Check required parameters
        command_instance.__check_required_options(options)
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
