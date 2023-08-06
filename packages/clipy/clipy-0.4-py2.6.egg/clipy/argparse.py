"""Utilities for defining commands based on argparse."""

import sys

argparse = __import__("argparse")

from clipy import command

__all__ = ["Command"]


class Command(command.Command):
    """Command."""

    usage = "%(prog)s [options]"

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.usage = self.usage
        return parser

    def parse_args(self, args):
        result = self.parser.parse_args(args)
        return result, []
