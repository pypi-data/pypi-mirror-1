"""Tests for clipy."""

import unittest

from clipy import command

__all__ = ["TestCommand",
           "TestCompositeCommand"]


class TestCommand(unittest.TestCase):
    """Tests for clipy.command.Command class."""

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

    def test_invokation(self):
        """Test command invokation."""
        self.command(["test"])
        self.assertTrue("dummy" in self.side_effect,
            "DummyCommand should provide side effect")

    def test_invokation_with_options(self):
        """Test command invokation with command options."""
        self.command(["test", "-f"])
        self.assertTrue("dummy" in self.side_effect,
            "DummyCommand should provide side effect")
        self.assertTrue("dummy_flag" in self.side_effect,
            "DummyCommand should provide side effect")


class CompositeCommand(command.CompositeCommand):

    def error(self, message):
        raise LookupError(message)


class TestCompositeCommand(unittest.TestCase):
    """Tests for clipy.command.CompositeCommand class."""

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

    def test_invokation(self):
        """Test composite command invokation."""
        self.composite_command(["test", "command"])
        self.assertTrue("dummy" in self.side_effect,
            "No effect from subcommand")

    def test_invokation_with_subcommand_options(self):
        """Test composite command invokation with subcommand options."""
        self.composite_command(["test", "command", "-f"])
        self.assertTrue("dummy" in self.side_effect,
            "No effect from subcommand")
        self.assertTrue("dummy_flag" in self.side_effect,
            "No effect from subcommand option")

    def test_invokation_with_composite_command_options(self):
        """Test composite command invokation with command options."""
        self.composite_command(["test", "-f", "command", "-f"])
        self.assertTrue("composite_flag" in self.side_effect,
            "No effect from composite command option")

    def test_no_subcommand_provided(self):
        """Test providing no subcommand to composite command invokation."""
        self.assertRaises(LookupError, self.composite_command, ["test"])

    def test_unknown_subcommand(self):
        """Test providing unknown subcommand to composite command invokation."""
        self.assertRaises(LookupError, self.composite_command, ["test", "hmmm"])


class DummyCommand(command.Command):

    def __init__(self):
        super(DummyCommand, self).__init__()
        self.was_executed = False

    def run(self):
        self.was_executed = True


dummy = DummyCommand()


class TestEntryPointCommandLoader(unittest.TestCase):
    """Tests for clipy.command.EntryPointLoader class."""

    # package clipy define this entry point, see setup.py
    entry_point = "clipy.test"

    def setUp(self):
        global dummy
        dummy.was_executed = False
        self.composite_command = CompositeCommand()

    def tearDown(self):
        global dummy
        dummy.was_executed = False

    def test_loading_commands(self):
        """Test loading commands with EntryPointCommandLoader."""
        loader = command.EntryPointCommandLoader(
            self.composite_command, self.entry_point)
        loader.load()

        self.composite_command(["test", "dummy"])
        global dummy
        self.assertTrue(dummy.was_executed, "Command was not executed")
