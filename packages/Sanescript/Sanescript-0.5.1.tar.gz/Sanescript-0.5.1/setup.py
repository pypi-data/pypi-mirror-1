
from setuptools import setup, find_packages

"""
Library for creating scripts with sub-commands, and options from the command
line, environment, and config files. This module is made up of two separate
entities:

    * Config framework
    * Scripting framework

Commands are specified which are essentially classes with a `__call__`
defined, and registered with the script. A command specifies the options
schema that it will have.
"""

setup(
    name = 'Sanescript',
    description = __doc__,
    version = '0.5.1',
    author='Ali Afshar',
    author_email='aafshar@gmail.com',
    packages = ['sanescript'],
    install_requires = ['pyyaml', 'argparse'],
)

