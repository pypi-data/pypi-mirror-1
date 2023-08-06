"""Tests for clipy."""

import unittest
import doctest

import pkg_resources

from clipy import command
from clipy import loader
from clipy import argparse
from clipy import utils

__all__ = ["TestCommand",
           "TestCompositeCommand"]


class DummyCommand(command.Command):

    def __init__(self):
        super(DummyCommand, self).__init__()
        self.was_executed = False

    def run(self, options, args, context=None):
        self.was_executed = True


dummy = DummyCommand()


class TestCase(unittest.TestCase):

    def shortDescription(self):
        return self.__doc__


class TestEntryPoint(pkg_resources.EntryPoint):

    def load(self):
        return pkg_resources.EntryPoint.load(self, require=False)


class TestLazyCommandRegistryLookup(TestCase):
    """Test LazyCommandRegistry lookup."""

    def setUp(self):
        self.obj = object()
        self.registry = utils.LazyCommandRegistry({
            "obj": self.obj,
            "ep_obj": utils.LazyCommand(factory=DummyCommand)
            })

    def runTest(self):
        global ep_obj
        self.assertTrue(self.registry["obj"] is self.obj, "Invalid lookup")
        self.assertTrue(isinstance(self.registry["ep_obj"], DummyCommand),
            "Invalid lookup")


class TestCommand(TestCase):

    def setUp(self):

        class DummyCommand(command.Command):

            def create_parser(self):
                parser = super(DummyCommand, self).create_parser()
                parser.add_option("-f", "--flag", action="store_true")
                return parser

            def run(self_, options, args, context=None):
                self.side_effect.append("dummy")
                if options.flag:
                    self.side_effect.append("dummy_flag")

        self.side_effect = []
        self.command = DummyCommand()


class TestCommandInvokation(TestCommand):
    """Test command invokation."""

    def runTest(self):
        self.command(["test"])
        self.assertTrue("dummy" in self.side_effect,
            "DummyCommand should provide side effect")


class TestCommandInvokationWithOptions(TestCommand):
    """Test command invokation with options."""

    def runTest(self):
        self.command(["test", "-f"])
        self.assertTrue("dummy" in self.side_effect,
            "DummyCommand should provide side effect")
        self.assertTrue("dummy_flag" in self.side_effect,
            "DummyCommand should provide side effect")


class CompositeCommand(command.CompositeCommand):

    def error(self, message):
        raise LookupError(message)


class TestCompositeCommand(TestCase):

    def setUp(self):
        class DummyCompositeCommand(CompositeCommand):

            def create_parser(self):
                parser = super(DummyCompositeCommand, self).create_parser()
                parser.add_option("-f", "--flag", action="store_true")
                return parser

            def run(self_, options, args, context=None):
                self.side_effect.append("composite")
                if options.flag:
                    self.side_effect.append("composite_flag")

        class DummyCommand(command.Command):

            def create_parser(self):
                parser = super(DummyCommand, self).create_parser()
                parser.add_option("-f", "--flag", action="store_true")
                return parser

            def run(self_, options, args, context=None):
                self.side_effect.append("dummy")
                if options.flag:
                    self.side_effect.append("dummy_flag")

        self.side_effect = []
        self.command = DummyCommand()
        self.composite_command = DummyCompositeCommand()
        self.composite_command.add_command("command", self.command)


class TestCompositeCommandInvokation(TestCompositeCommand):
    """Test composite command invokation."""

    def runTest(self):
        self.composite_command(["test", "command"])
        self.assertTrue("dummy" in self.side_effect,
            "No effect from subcommand")


class TestCompositeCommandInvokationWithSubcommandOptions(TestCompositeCommand):
    """Test composite command invokation with subcommand options."""

    def runTest(self):
        self.composite_command(["test", "command", "-f"])
        self.assertTrue("dummy" in self.side_effect,
            "No effect from subcommand")
        self.assertTrue("dummy_flag" in self.side_effect,
            "No effect from subcommand option")


class TestCompositeCommandInvokationWithCommandOptions(TestCompositeCommand):
    """Test composite command invokation with command options."""

    def runTest(self):
        self.composite_command(["test", "-f", "command"])
        self.assertTrue("composite_flag" in self.side_effect,
            "No effect from composite command option")


class TestEntryPointCommandLoader(TestCase):
    """Test loading commands via entry points with EntryPointCommandLoader."""

    # package clipy define this entry point, see setup.py
    entry_point = "clipy.test"

    def setUp(self):
        global dummy
        dummy.was_executed = False
        self.composite_command = CompositeCommand()

    def tearDown(self):
        global dummy
        dummy.was_executed = False

    def runTest(self):
        ldr = loader.EntryPointCommandLoader(
            self.composite_command, self.entry_point)
        ldr.load()

        self.composite_command(["test", "dummy"])
        global dummy
        self.assertTrue(dummy.was_executed, "Command was not executed")


class TestArgparseCommand(TestCase):

    def setUp(self):

        class DummyCommand(argparse.Command):

            def create_parser(self):
                parser = super(DummyCommand, self).create_parser()
                parser.add_argument("-f", "--flag", action="store_true")
                parser.add_argument("arg", action="store", nargs="?")
                return parser

            def run(self_, options, args, context=None):
                self.side_effect.append("dummy")
                if options.flag:
                    self.side_effect.append("dummy_flag")
                if options.arg:
                    self.side_effect.append("dummy_arg")

        self.side_effect = []
        self.command = DummyCommand()


class TestArgparseCommandInvokation(TestArgparseCommand, TestCommandInvokation):
    """Test powered command invokation."""


class TestArgparseCommandInvokationWithOptions(TestArgparseCommand,
                                    TestCommandInvokationWithOptions):
    """Test powered command invokation with options."""


class TestArgparseCommandInvokationWithArgs(TestArgparseCommand):
    """Test powered command invokation with args."""

    def runTest(self):
        self.command(["test", "arg"])
        self.assertTrue("dummy" in self.side_effect,
            "DummyCommand should provide side effect")
        self.assertTrue("dummy_arg" in self.side_effect,
            "DummyCommand should provide side effect")

        self.command(["test", "-f", "arg"])
        self.assertTrue("dummy_flag" in self.side_effect,
            "DummyCommand should provide side effect")


def test_suite():
    from clipy import tests
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    suite.addTest(doctest.DocFileSuite("help.txt"))
    suite.addTest(doctest.DocFileSuite("composite.txt"))
    return suite
