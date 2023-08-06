# -*- coding: utf-8 -*-

"""
    sanescript.script
    ~~~~~~~~~~~~~~~~~

    Define scripts with multiple subcommands that collate configuration from
    multiple sources.

    :copyright: 2009-2010 Ali Afshar <aafshar@gmail.com>
    :license: MIT
"""


import sys, os

from config import Config, Option
from parsing import Parser


class _Command(object):
    """The base command class"""

    name = None

    options = []

    def __init__(self, script):
        self._script = script
        self.name = self.__class__.name or self.__class__.__name__.lower()
        self.options = list(self.options)

    def __call__(self, config):
        raise NotImplementedError('Command %r has no call defined.' % self.name)


class Command(_Command):
    """This command has no documentation."""


class Script(object):

    pre_options = [
        Option('config_file', help='The config file to use'),
    ]

    options = [
    ]

    env_prefix = None

    def __init__(self, env_prefix=None):
        self._global_options = []
        self._commands = {}
        self._parser = Parser(self.pre_options)
        self._config = Config(self._parser, env_prefix or self.env_prefix)
        # XXX Workaround for argparse, we have already added the preoptions to
        # the parser, but now we add them again to the Config, the __pre__ tag
        # prevents the config adding them again to the parser.
        self._config.add_options(self.pre_options, '__pre__')
        self._config.add_options(self.options, None)

    def add_command_instance(self, command):
        self._commands[command.name] = command
        self._parser.add_command(command)
        self._config.add_options(command.options, prefix=command.name)

    def add_command(self, command_type, **kw):
        command = command_type(self, **kw)
        self.add_command_instance(command)

    def execute(self, argv, env, config_files):
        config_files = self._calculate_config_files(argv, env, config_files)
        self._prime_config(argv, config_files)
        command = self._commands.get(self._config.__command__)
        return command(self._config)

    def main(self, argv=list(sys.argv), env=os.environ.copy(), config_files=None):
        return self.execute(argv, env, config_files)

    def _calculate_config_files(self, argv, env, config_files):
        # config file might be specified in argv or env
        self._config.grab_from_env(env)
        self._config.pregrab_from_argv(argv[1:])
        if config_files is None:
            config_files = []
        if self._config.config_file:
            config_files.append(self._config.config_file)
        return config_files

    def _prime_config(self, argv, config_files):
        for config_file in config_files:
            self._config.grab_from_file(config_file)
        self._config.grab_from_env()
        self._parser.update(self._config.to_dict())
        self._config.grab_from_argv(argv[1:])





