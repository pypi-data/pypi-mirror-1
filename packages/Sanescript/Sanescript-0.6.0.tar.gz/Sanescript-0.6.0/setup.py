# -*- coding: utf-8 -*-

"""
    setup
    ~~~~~

    Sanescript build/isntallation script.

    :copyright: 2009-2010 Ali Afshar aafshar@gmail.com
    :license: MIT
"""
from setuptools import setup, find_packages

description = """Library for creating scripts with sub-commands, and options from the command
line, environment, and config files."""

long_description = """
This module is made up of two separate
entities:

    * Config framework
    * Scripting framework

Commands are specified which are essentially classes with a `__call__`
defined, and registered with the script. A command specifies the options
schema that it will have.
"""

setup(
    name = 'Sanescript',
    description = description,
    long_description = description + long_description,
    version = '0.6.0',
    author='Ali Afshar',
    author_email='aafshar@gmail.com',
    packages = ['sanescript'],
    install_requires = ['pyyaml', 'argparse'],
)

