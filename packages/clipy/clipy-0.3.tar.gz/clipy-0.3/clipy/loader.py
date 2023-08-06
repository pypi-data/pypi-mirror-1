"""Command loader."""

import pkg_resources

__all__ = ["BaseCommandLoader",
           "EntryPointCommandLoader"]


class BaseCommandLoader(object):
    """Command loader for composite commands.

    This is a base class, your need to subclass it and provide :meth:`load`
    method.
    """

    def __init__(self, composite_command):
        """Initialize CommandLoader.

        :param composite_command: Composite command to load commands for.
        :type composite_command: :class:`CompositeCommand`
        """
        self.composite_command = composite_command

    def load(self):
        """Load commands."""
        raise NotImplementedError()


class EntryPointCommandLoader(BaseCommandLoader):
    """Command loader that loads commands via setuptools entry point."""

    def __init__(self, composite_command, entry_point):
        """Initialize EntryPointCommandLoader.

        :param composite_command: Composite command to load commands for.
        :type composite_command: :class:`CompositeCommand`

        :param entry_point: Entry point group name to load commands from.
        :type entry_point: str
        """
        super(EntryPointCommandLoader, self).__init__(composite_command)
        self.entry_point = entry_point

    def load(self):
        for entry_point in pkg_resources.iter_entry_points(self.entry_point):
            self.composite_command.add_command(entry_point.name, entry_point)
