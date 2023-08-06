"""Base classes for defining commands.

There are two classes for commands: Command and CompositeCommand. First one is
using for defining simple commands and second is for commands with subcommands
(you might think of svn for example).
"""

import sys
import getpass
import optparse

import pkg_resources

__all__ = ["Command",
           "CompositeCommand"]


missing = object()


class LazyRegistry(object):
    """Object with dict-like interface for storing references to objects.

    This object acts like dict but treat :class:`pkg_resources.EntryPoint`
    values specially by loading them on first access.
    """

    def __init__(self, storage=None):
        if storage is None:
            storage = {}
        self.storage = storage

    def __getitem__(self, name):
        value = self.storage[name]
        if isinstance(value, pkg_resources.EntryPoint):
            value = value.load()
            self.storage[name] = value
        return value

    def __setitem__(self, name, value):
        self.storage[name] = value

    def __contains__(self, value):
        return value in self.storage

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default


class Command(object):
    """Simple command."""

    usage = "%prog [options]"
    summary = ""

    def __init__(self):
        """Initialize command."""
        self.parser = None
        self.options = None
        self.args = None
        self.context = None
        self.parent = None

    def create_parser(self):
        """Create parser for command.

        This implementation returns optparse.OptionParser, but you can use your
        own as long as you define :meth:`parse_args` method yourself.
        """
        parser = optparse.OptionParser()
        parser.usage = self.usage
        return parser

    def parse_args(self, args):
        """Parse args and return pair of options, arguments."""
        return self.parser.parse_args(args)

    def run(self):
        """Run command.

        By default this method throws error.
        """
        self.error("This command is not implemented yet.")

    def __call__(self, args=None, context=None, parent=None):
        """Parse arguments and run command."""
        if args is None:
            args = sys.argv
        args = args[1:]

        self.context = context
        self.parent = parent

        self.parser = self.create_parser()
        options, args = self.parse_args(args)

        self.options = options
        self.args = args

        self.run()

    def print_help(self):
        self.parser.print_help()

    def print_usage(self):
        self.parser.print_usage()

    def error(self, message):
        self.parser.error(message)

    def ask(self, prompt, default=True, careful=False):
        """Ask user.

        This method originally based on PasteScript code.
        """
        if careful:
            prompt += ' [yes/no]?'
        elif default == 'none':
            prompt += ' [y/n]?'
        elif default:
            prompt += ' [Y/n]? '
        else:
            prompt += ' [y/N]? '
        while 1:
            response = raw_input(prompt).strip().lower()
            if not response:
                if careful:
                    print 'Please enter yes or no'
                    continue
                return default
            if careful:
                if response in ('yes', 'no'):
                    return response == 'yes'
                print 'Please enter "yes" or "no"'
                continue
            if response[0].lower() in ('y', 'n'):
                return response[0].lower() == 'y'
            print '"y" or "n" please'

    def challenge(self, prompt, default=missing, echo=True):
        """Prompt the user for a variable.

        This method originally based on PasteScript code.
        """
        if default is not missing:
            prompt += ' [%r]' % default
        prompt += ': '
        while 1:
            if echo:
                prompt_method = raw_input
            else:
                prompt_method = getpass.getpass
            response = prompt_method(prompt).strip()
            if not response:
                if default is not missing:
                    return default
                else:
                    continue
            else:
                return response


class CompositeCommand(Command):
    """Composite command."""

    def __init__(self, commands=None, registry_cls=None):
        """Initialize composite command.

        :param commands: Dictonary-like object with commands.
        :type commands: dict
        """
        if registry_cls is None:
            registry_cls = LazyRegistry
        if commands is None:
            commands = {}
        self.commands = LazyRegistry(commands)
        super(CompositeCommand, self).__init__()

    def add_command(self, name, command):
        """Add command.

        :param name: Name of command.
        :type name: str

        :param command: Command instance.
        :type command: :class:`Command`
        """
        if name in self.commands:
            raise ValueError("command already registered")
        self.commands[name] = command

    def execute_command(self, name, args, context=None):
        """Execute command."""
        command = self.commands.get(name, None)
        if command is None:
            self.error("Uknown subcommand")
        command(args, context=None)

    def create_parser(self):
        """Create parser for composite command.

        The main idea is the same as in :class:`clipy.command.Command`, but
        there is few more restrictions -- parser should return unparsed
        arguments untouched, cause subcommand name is extracted from it.
        """
        parser = super(CompositeCommand, self).create_parser()
        parser.disable_interspersed_args()
        return parser

    def get_context(self):
        """Return context for subcommands.

        If you want to provide context for subcommands based on command's
        options this method should return some object, there is no restriction
        on its type. By default it returns None.
        """
        return None

    def run(self):
        """Run composite command.

        By default this command do nothing. But if you want to do some things
        except dispatching to subcommands, you should place your code here.
        """
        pass

    def __call__(self, args=None, context=None, parent=None):
        """Parse arguments, run command and dispatch to subcommands."""
        if args is None:
            args = sys.argv
        assert len(args), "Wrong arguments"

        self.context = context
        self.parent = parent

        prog_name, args = args[0], args[1:]
        self.parser = self.create_parser()
        options, args = self.parse_args(args)

        if not args:
            self.error("Please provide subcommand")

        subcommand_name = args[0]
        if not subcommand_name in self.commands:
            self.error("Uknown subcommand")

        subcommand = self.commands[subcommand_name]

        self.options = options
        self.args = []
        self.run()

        context = self.get_context()

        subcommand(args, context=context, parent=self)
