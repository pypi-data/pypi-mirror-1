"""Utilities."""

import itertools

__all__ = ["LazyCommandRegistry",
           "LazyCommand"]


class LazyCommandRegistry(object):

    def __init__(self, storage=None):
        if storage is None:
            storage = {}
        self.storage = storage

    def __getitem__(self, name):
        value = self.storage[name]
        if isinstance(value, LazyCommand):
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

    def keys(self):
        return self.storage.keys()

    def values(self):
        return (self.get(n) for n in self.keys())

    def items(self):
        return itertools.izip(self.keys(), self.values())


class LazyCommand(object):

    def __init__(self, factory):
        self.factory = factory
        self.registration = None

    def load(self):
        command = self.factory()
        if self.is_registered:
            name, parent = self.registration
            command.register(name, parent)
        return command

    def register(self, name, parent):
        self.registration = name, parent

    @property
    def is_registered(self):
        return not self.registration is None
