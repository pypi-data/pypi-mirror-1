#!/usr/bin/env python
#
#   command.py
#   progtools
#
#   Copyright (C) 2008-2009 Ross Light
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#

"""
Program command modes

These commands are for simulating programs like Subversion or APT that use sub-
commands to perform an operation.  The implementation closely resembles
`Bazaar's`_ infrastructure.

.. _Bazaar's: Bazaar_
.. _Bazaar: http://bazaar-vcs.org/
"""

import sys

from progtools import errors, program

__author__ = 'Ross Light'
__date__ = 'December 7, 2008'
__docformat__ = 'reStructuredText'
__license__ = 'MIT'
__all__ = ['CommandMeta',
           'Command',
           'HelpCommand',
           'Registry',]

def _cleandoc(docstring):
    """Filters a docstring to a parseable form."""
    # Note: This is copied from inspect, public domain.
    lines = docstring.expandtabs().splitlines()
    # Find minimum indentation of any non-blank lines after first line.
    margin = sys.maxint
    for line in lines[1:]:
        content = len(line.lstrip())
        if content:
            indent = len(line) - content
            margin = min(margin, indent)
    # Remove indentation.
    if lines:
        lines[0] = lines[0].lstrip()
    if margin < sys.maxint:
        for i in xrange(1, len(lines)):
            lines[i] = lines[i][margin:]
    # Remove any trailing or leading blank lines.
    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)
    return '\n'.join(lines)

def _parse_documentation(docstring):
    """
    Parse help from a command class's docstring.
    
    :Parameters:
        docstring : str
            The class's docstring
    :Returns: The synopsis and description of the command
    :ReturnType: tuple
    """
    lines = docstring.splitlines()
    try:
        break_index = lines.index('')
    except ValueError:
        # No big break, so we just have usage
        synopsis, description = '\n'.join(lines), None
    else:
        synopsis = '\n'.join(lines[:break_index])
        description = '\n'.join(lines[break_index + 1:])
    return (synopsis, description)

def _parse_command_name(class_name):
    if class_name.lower().startswith('cmd_'):
        # Bazaar-style command name
        return class_name[4:].replace('_', '-')
    elif class_name.endswith('Command'):
        # MyCamel_Case_Command => mycamel-case
        return class_name[:-7].rstrip('_').lower().replace('_', '-')
    else:
        # Use class name as a last resort
        return class_name.lower().replace('_', '-')

class CommandMeta(type):
    """
    Metaclass for all commands.
    
    This primarily exists so that attributes of commands are automatically
    filled out.
    """
    def __new__(cls, name, bases, class_dict):
        # Parse name automatically
        class_dict.setdefault('name', _parse_command_name(name))
        # Retrieve synopsis and description from docstring
        docstring = _cleandoc(class_dict.get('__doc__', ''))
        if docstring:
            synopsis, description = _parse_documentation(docstring)
            class_dict.setdefault('synopsis', synopsis)
            class_dict.setdefault('description', description)
        # Set default attributes
        class_dict.setdefault('aliases', ())
        class_dict.setdefault('usage', None)
        # Create class
        return super(CommandMeta, cls).__new__(cls, name, bases, class_dict)

class Command(object):
    """
    A program's subcommand.
    
    Override the docstring to write the documentation for the command.
    
    :CVariables:
        name : str
            The canonical name for the command.  If not given, then the name is
            derived from the class name.
            
            The class name derivation comes from one of the formats: ``cmd_*``,
            ``*Command``, or simply the command's name.  In all cases, all
            underscores are replaced with hyphens.  The second and third
            formats change the name to lowercase.
        usage : str
            The usage for the command.
        synopsis : str
            The basic purpose for the command.  If not given, then the synopsis
            is taken from the first line of the docstring.
        description : str
            The description of the command.  If not given, then the description
            is taken from the remaining lines of the docstring.
        aliases : tuple of str
            Aliases for the command.  Not inherited.
    """
    __metaclass__ = CommandMeta
    name = None
    usage = None
    aliases = ()
    
    def add_options(self, parser):
        """
        Adds all command-specific options to the parser.
        
        Override in subclasses to add options and defaults.
        
        :Parameters:
            parser : optparse.OptionParser
                The parser to add options to
        """
        pass
    
    def run_with_argv(self, argv=None, parser=None, verbose=True):
        """
        Parses arguments and executes the command.
        
        :Parameters:
            argv : list of str
                Command-line arguments without the program name.  Defaults to
                ``sys.argv[1:]``.
        :Keywords:
            parser : optparse.OptionParser
                The parser to use.  If not given, one will be created for the
                command.  You can use this to add global options.
            verbose : bool
                Whether to display error messages if the command raises an
                error.
        :Returns: A status code
        :ReturnType: int
        :See: run
        """
        # Get default parameters
        if argv is None:
            argv = sys.argv[1:]
        if parser is None:
            parser = program.OptionParser()
        # Parse arguments
        self.add_options(parser)
        options, args = parser.parse_args(argv)
        args = args[1:]  # trim command name
        if not parser.allow_interspersed_args:
            # We stopped because of the command. Remove it and proceed.
            options, args = parser.parse_args(args, options)
        # Run command
        return program.saferun(self.run, [args, options],
                               usage=self.usage, verbose=verbose)
    
    def run(self, args, options):
        """
        Executes the command.
        
        Override this in subclasses to execute the command.
        
        Users of the command should call `run_with_argv`, not this method.
        
        :Raises NotImplementedError: If not overridden
        :See: run_with_argv
        """
        raise NotImplementedError()
    
    def __repr__(self):
        return "%s()" % (type(self).__name__)
    
    def __str__(self):
        return self.name

class HelpCommand(Command):
    """Display documentation for a command."""
    usage = "help [command]"
    
    def __init__(self, registry, program_usage=None):
        self.registry = registry
        self.program_usage = program_usage
    
    def run(self, args, options):
        if len(args) == 0:
            if self.program_usage:
                program_name = program.get_program_name()
                usage = self.program_usage.replace('%prog', program_name)
                if not usage.lower().startswith('usage:'):
                    usage = 'usage: ' + usage
                print usage
            else:
                print "No documentation"
        elif len(args) == 1:
            if args[0] == 'commands':
                self._list_commands()
            else:
                self._display_help(args[0])
        else:
            raise errors.UsageError()
    
    def _list_commands(self):
        cmp_func = (lambda x, y: cmp(x.name.lower(), y.name.lower()))
        # Sort commands by name
        command_list = self.registry.get_command_list()
        command_list.sort(cmp_func)
        # Get longest name (for formatting)
        max_name_length = 0
        for command in command_list:
            max_name_length = max(max_name_length, len(command.name))
        # Display all commands
        for command in command_list:
            if command.synopsis:
                print "%-*s  %s" % (max_name_length, command.name,
                                    command.synopsis)
            else:
                print command.name
    
    def _display_help(self, name):
        # Retrieve command
        try:
            command = self.registry.get_command(name)
        except KeyError:
            print >> sys.stderr, "help: Command '%s' does not exist" % (name)
            return
        # Print synopsis
        if command.synopsis:
            print "%s - %s" % (command.name, command.synopsis)
        else:
            print command.name
        # Print usage
        if command.usage:
            print "Usage:", command.usage
        # Print aliases
        if command.aliases:
            print "Aliases:", ', '.join(command.aliases)
        # Print description
        if command.description:
            print
            print "Description:"
            print command.description
        # Print placeholder if we have no documentation
        if not command.synopsis and \
           not command.usage and \
           not command.description:
            print "No documentation"

class Registry(object):
    """The command collection."""
    
    def __init__(self):
        self.__commands = {}
    
    def _register(self, name, command):
        if name not in self.__commands:
            self.__commands[name] = command
        else:
            raise errors.AlreadyRegisteredError(name)
    
    def register(self, command):
        """
        Registers a command.
        
        :Parameters:
            command
                The command to add.  This may be a command class or instance.
        :Raises KeyError: If a command with that name already is registered
        """
        # Initialize command from class
        if isinstance(command, type):
            command = command()
        # Register command
        self._register(command.name, command)
        for alias in command.aliases:
            self._register(alias, command)
    
    def unregister(self, command):
        """
        Removes a command from the registration list.
        
        :Parameters:
            command : type
                The command's class
        :Raises KeyError: If the command has not been registered
        """
        key_list = [key for key in self.__commands
                    if type(self.__commands[key]) == command]
        if not key_list:
            raise KeyError(command.name)
        for key in key_list:
            del self.__commands[key]
    
    def get_command(self, name):
        """
        Retrieves a command for a name.
        
        The name given may be an alias.
        
        :Parameters:
            name : str
                The name of the command
        :Raises KeyError: If no command exists for that name
        :Returns: An initialized command
        :ReturnType: `Command`
        """
        return self.__commands[name]
    
    def get_command_list(self):
        """
        Retrieves all command objects registered.
        
        :Returns: The command objects
        :ReturnType: list
        """
        result = []
        for command in self.__commands.itervalues():
            if command not in result:
                result.append(command)
        return result

def run(registry, argv=None, parser=None):
    """
    Does a simple run of the command.
    
    :Parameters:
        registry : `Registry`
            The command registry to run with
        argv : list of str
            Command-line arguments without the program name.  Defaults to
            ``sys.argv[1:]``.
    :Keywords:
        parser : optparse.OptionParser
            The parser to use.  If not given, one will be created for the
            command.  You can use this to add global options.
    """
    # Retrieve command-line arguments
    if argv is None:
        argv = sys.argv[1:]
    # Get command name
    if parser is None:
        # We don't have any global options.  The command name should be first.
        command_name = argv[0]
    else:
        # Exploit the parser to get the command name
        old_setting = parser.allow_interspersed_args
        parser.allow_interspersed_args = False
        options, args = parser.parse_args(argv)
        command_name = args[0]
        parser.allow_interspersed_args = old_setting
        del options, args, old_setting
    # Run command
    try:
        command = registry.get_command(command_name)
    except KeyError:
        raise errors.UsageError("Command '%s' does not exist" % command_name)
    else:
        return command.run_with_argv(argv, parser=parser)
