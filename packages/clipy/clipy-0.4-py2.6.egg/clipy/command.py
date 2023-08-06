"""Base classes for defining commands.
"""

import sys
import getpass
import optparse

import pkg_resources

from clipy import utils

__all__ = ["Command",
           "CompositeCommand",
           "UIMethods",
           "HelpCommand"]


class UIMethods(object):
    """Methods for creating command line user interfaces."""

    missing = object()

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
        if default is not self.missing:
            prompt += ' [%r]' % default
        prompt += ': '
        while 1:
            if echo:
                prompt_method = raw_input
            else:
                prompt_method = getpass.getpass
            response = prompt_method(prompt).strip()
            if not response:
                if default is not self.missing:
                    return default
                else:
                    continue
            else:
                return response


class Command(UIMethods):
    """Simple command."""

    usage = "%prog [options]"
    summary = ""

    def __init__(self, summary=None):
        """Initialize command.

        :keyword summary: Summary for command.
        :type summary: str
        """
        self.options = None
        self.args = None
        self.context = None

        self._parent = None
        self._name = None

        if summary:
            self.summary = summary

        self.parser = self.create_parser()

    @property
    def full_name(self):
        """Full name of the command contains parent's name"""
        if self.is_registered:
            return "%s %s" % (self.parent.name, self._name)
        else:
            return sys.argv[0]

    @property
    def name(self):
        """Name of the command."""
        if self.is_registered:
            return self._name
        else:
            return sys.argv[0]

    @property
    def parent(self):
        """Parent command or None if command has no parent."""
        return self._parent

    def register(self, name, parent):
        """Register command as subcommand.

        After registration command has its :attr:`name` and :attr:`full_name`
        different and :attr:`parent` set to :param:`parent`.

        :param name: Name of the command to register as.
        :type name: str

        :param parent: Parent command.
        :type parent: :class:`CompositeCommand`
        """
        if self.is_registered:
            raise ValueError("Command already registered")
        self._parent = parent
        self._name = name

    @property
    def is_registered(self):
        """Indicate if command was registered as subcommand."""
        return not self.parent is None

    def create_parser(self):
        """Create parser for command.

        This implementation returns optparse.OptionParser, but you can use your
        own as long as you define :meth:`parse_args` method yourself.
        """
        parser = optparse.OptionParser()
        parser.usage = self.usage
        parser.get_prog_name = lambda: self.full_name
        return parser

    def parse_args(self, args):
        """Parse args and return pair of options, arguments."""
        return self.parser.parse_args(args)

    def run(self, options, args, context=None):
        """Run command.

        By default this method throws error.
        """
        self.error("This command is not implemented yet.")

    def print_help(self):
        """Print help for command."""
        self.parser.print_help()

    def print_usage(self):
        """Print usage for command."""
        self.parser.print_usage()

    def error(self, message):
        """Throw error.

        :param message: Message to print to stderr.
        :type message: str
        """
        self.parser.error(message)

    def __call__(self, args=None, context=None):
        """Parse arguments and run command.

        :keyword args: Arguments to call command with, if None is provided -
        sys.argv will be used instead.
        :type args: [str]

        :keyword context: Context command is calling in. This context can be
        provided by composite commands to its subcommands with
        :meth:`get_context`.
        :type context: object
        """
        if args is None:
            args = sys.argv
        args = args[1:]
        options, args = self.parse_args(args)
        self.run(options, args, context=context)


class HelpCommand(Command):
    """Help command for composite commands."""

    summary = "print help and exit"

    def print_command_help(self):
        print "Commands:"
        for name, command in self.parent.commands.items():
            print "  %s %s" % (name.ljust(11, " "), command.summary)

    def print_br(self):
        print

    def run(self, options, args, context=None):
        if self.is_registered:
            self.parent.parser.print_help()
            self.print_br()
            self.print_command_help()
        else:
            self.error("This command can be used only as subcommand.")


class CompositeCommand(Command):
    """Composite command."""

    def __init__(self, commands=None, registry_cls=None, summary=None,
            add_help_command=True):
        """Initialize composite command.

        :param commands: Dictonary-like object with commands.
        :type commands: dict
        """
        super(CompositeCommand, self).__init__(summary=summary)
        if registry_cls is None:
            registry_cls = utils.LazyCommandRegistry
        self.commands = registry_cls()
        if not commands is None:
            for name, command in commands.items():
                self.add_command(name, command)
        if add_help_command:
            self.add_command("help", HelpCommand())

    def print_help(self):
        if "help" in self.commands:
            self.execute_command("help", [])
        else:
            self.parser.print_help()

    def add_command(self, name, command):
        """Add command.

        :param name: Name of command.
        :type name: str

        :param command: Command instance.
        :type command: :class:`Command`
        """
        if name in self.commands:
            raise ValueError("command already registered")
        command.register(name, self)
        self.commands[name] = command

    def execute_command(self, name, args, context=None):
        """Execute command.

        :param name: Name of the command to execute.
        :type name: str

        :param args: Arguments to pass to the command __call__ method.
        :type args: [str]

        :keyword context: Context command is calling in.
        :type context: object
        """
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
        parser = optparse.OptionParser(add_help_option=False)
        parser.disable_interspersed_args()
        parser.get_prog_name = lambda: self.full_name
        parser.add_option("-h", "--help", action="store_true")
        return parser

    def get_context(self, options, args, context=None):
        """Return context for subcommands.

        If you want to provide context for subcommands based on command's
        options this method should return some object, there is no restriction
        on its type. By default it returns None.
        """
        return None

    def run(self, options, args, context=None):
        """Run composite command.

        By default this command do nothing. But if you want to do some things
        except dispatching to subcommands, you should place your code here.
        """
        pass

    def no_command(self, options, args, context=None):
        """This method is called when composite command have no subcommand
        provided with arguments.
        """
        if not options.help:
            self.print_help()
            self.error("No command provided.")

    def unknown_command(self, options, args, context=None):
        """This method is called when composite command have unknown subcommand.
        """
        self.print_help()
        self.error("Unknown command provided.")

    def __call__(self, args=None, context=None):
        """Parse arguments, run command and dispatch to subcommands."""
        if args is None:
            args = sys.argv
        assert len(args), "Wrong arguments"

        prog_name, args = args[0], args[1:]
        options, args = self.parse_args(args)

        self.run(options, args, context=context)

        if options.help:
            self.print_help()

        if args:
            subcommand_name = args[0]
            if not subcommand_name in self.commands:
                self.unknown_command(options, args, context=context)
            else:
                context = self.get_context(options, args, context=context)
                subcommand = self.commands[subcommand_name]
                subcommand(args, context=context)
        else:
            self.no_command(options, args, context=context)
