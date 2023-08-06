# -*- coding: utf-8 -*-

"""
    sanescript
    ~~~~~~~~~~

    Easily define scripts which get options from multiple sources, and has
    multiple sub commands.

    :copyright: 2009-2010 Ali Afshar <aafshar@gmail.com>
    :license: MIT
"""

from main import register, main
from config import Config, Option, UNSET
from script import Script, Command
from processing import processors


__all__ = ['Command', 'register', 'Option', 'Config', 'main', 'UNSET']

