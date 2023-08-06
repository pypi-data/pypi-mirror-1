"""Tests for clipy."""

import unittest

import pkg_resources

from clipy import command
from clipy import loader
from clipy import argparse

__all__ = ["TestCommand",
           "TestCompositeCommand"]


class TestCase(unittest.TestCase):

    def shortDescription(self):
        return self.__doc__


ep_obj = object()


class TestEntryPoint(pkg_resources.EntryPoint):

    def load(self):
        return pkg_resources.EntryPoint.load(self, require=False)


class TestLazyRegistryLookup(TestCase):
    """Test LazyRegistry lookup."""

    def setUp(self):
        self.obj = object()
        self.registry = command.LazyRegistry({
            "obj": self.obj,
            "ep_obj": TestEntryPoint("ep_obj", "clipy.tests", attrs=["ep_obj"])
            })

    def runTest(self):
        global ep_obj
        self.assertTrue(self.registry["obj"] is self.obj, "Invalid lookup")
        self.assertTrue(self.registry["ep_obj"] is ep_obj, "Invalid lookup")


class TestCommand(TestCase):

    def setUp(self):

        class DummyCommand(command.Command):

            def create_parser(self):
                parser = super(DummyCommand, self).create_parser()
                parser.add_option("-f", "--flag", action="store_true")
                return parser

            def run(self_):
                self.side_effect.append("dummy")
                if self_.options.flag:
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

            def run(self_):
                self.side_effect.append("composite")
                if self_.options.flag:
                    self.side_effect.append("composite_flag")

        class DummyCommand(command.Command):

            def create_parser(self):
                parser = super(DummyCommand, self).create_parser()
                parser.add_option("-f", "--flag", action="store_true")
                return parser

            def run(self_):
                self.side_effect.append("dummy")
                if self_.options.flag:
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


class TestCompositeCommandNoSubcommand(TestCompositeCommand):
    """Test providing no subcommand to composite command invokation."""

    def runTest(self):
        self.assertRaises(LookupError, self.composite_command, ["test"])


class TestCompositeCommandUnknownSubcommand(TestCompositeCommand):
    """Test providing unknown subcommand to composite command invokation."""

    def runTest(self):
        self.assertRaises(LookupError, self.composite_command, ["test", "hmmm"])


class DummyCommand(command.Command):

    def __init__(self):
        super(DummyCommand, self).__init__()
        self.was_executed = False

    def run(self):
        self.was_executed = True


dummy = DummyCommand()


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

            def run(self_):
                self.side_effect.append("dummy")
                if self_.options.flag:
                    self.side_effect.append("dummy_flag")
                if self_.options.arg:
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
