"""Base classes for defining commands.

There are two classes for commands: Command and CompositeCommand. First one is
using for defining simple commands and second is for commands with subcommands
(you might think of svn for example).
"""

import sys
import optparse

__all__ = ["Command",
           "CompositeCommand"]


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

    def __call__(self, args=None, context=None):
        """Parse arguments and run command."""
        if args is None:
            args = sys.argv
        self.context = context
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


class CompositeCommand(Command):
    """Composite command."""

    def __init__(self, commands=None):
        """Initialize composite command.

        :param commands: Dictonary-like object with commands.
        :type commands: dict
        """
        if commands is None:
            commands = {}
        self.commands = commands
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
        on its type.
        """
        return None

    def run(self):
        """Run composite command.

        By default this command do nothing. But if you want to do some things
        except dispatching to subcommands, you should place your code here.
        """
        pass

    def __call__(self, args=None):
        """Parse arguments, run command and dispatch to subcommands."""
        if args is None:
            args = sys.argv
        assert len(args), "Wrong arguments"
        prog_name, args = args[0], args[1:]
        self.parser = self.create_parser()
        options, args = self.parse_args(args)
        if not args:
            self.error("Please provide subcommand")
        subcommand_name = args.pop(0)
        if not subcommand_name in self.commands:
            self.error("Uknown subcommand")
        subcommand = self.commands[subcommand_name]

        self.options = options
        self.args = []
        self.run()

        context = self.get_context()

        subcommand(args, context=context)
