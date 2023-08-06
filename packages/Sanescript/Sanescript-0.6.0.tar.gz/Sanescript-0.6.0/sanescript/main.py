# -*- coding: utf-8 -*-

"""
    sanescript.main
    ~~~~~~~~~~~~~~~

    Provides the default singleton behaviour for a single script (ie most
    cases).

    :copyright: 2009-2010 Ali Afshar aafshar@gmail.com
    :license: MIT
"""

from script import Script


# global script instance
_script = Script()


def register_instance(command):
    """Register a command instance with the global script instance.
    """
    _script.add_command_instance(command)


def register(command_type):
    """Register a command class with the global script instance.
    """
    _script.add_command(command_type)


def main(*args, **kw):
    """Execute the global script isntance.
    """
    return _script.main(*args, **kw)

