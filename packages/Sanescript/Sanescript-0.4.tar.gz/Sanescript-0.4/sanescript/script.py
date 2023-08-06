
"""
sanescript.script
~~~~~~~~~~~~~~~~~
"""

import sys, os

from argparse import ArgumentParser

from config import Config, Option


class _Command(object):
    """The base command class"""

    name = None

    options = []

    include_interactive = ()
    exclude_interactive = ()

    def __init__(self, script):
        self._script = script
        self.name = self.__class__.name or self.__class__.__name__.lower()
        self.options = list(self.options)

    def __call__(self, config):
        raise NotImplementedError('Command %r has no call defined.' % self.name)


class Command(_Command):
    """This command has no documentation."""


class Script(object):

    options = [
        Option('config_file', help='The config file to use'),
        Option('interactive', help='Get the options interactively',
                short_name='I', action='store_true'),
    ]

    env_prefix = None

    def __init__(self, env_prefix=None):
        self._global_options = []
        self._commands = {}
        self._parser = ArgumentParser()
        self._config = Config(self._parser, env_prefix or self.env_prefix)
        self._subparser_factory = self._parser.add_subparsers(dest='__command__')
        self.add_options(self.options, None)

    def add_options(self, options, prefix):
        for option in options:
            self.add_option(option, prefix)

    def add_option(self, option, prefix):
        self._config.add_option(option, prefix, self._parser)

    def add_command_instance(self, command):
        parser = self._subparser_factory.add_parser(command.name, help=command.__doc__)
        self._commands[command.name] = command
        for option in command.options:
            self._config.add_option(option, command.name, parser)

    def add_command(self, command_type, **kw):
        command = command_type(self, **kw)
        self.add_command_instance(command)

    def execute(self, argv, env, config_files):
        # config file might be specified in argv or env
        self._config.grab_from_env(env)
        self._config.grab_from_argv(argv[1:])
        if config_files is None:
            config_files = []
        if self._config.config_file:
            config_files.append(self._config.config_file)
        self._prime_config(argv, config_files)
        command = self._commands.get(self._config.__command__)
        if self._config.interactive:
            self._config.grab_from_interactive(self._config.__command__,
                                               command.include_interactive,
                                               command.exclude_interactive)
        if self._config.ensure_required():
            return command(self._config)
        else:
            print self._parser.print_help()

    def _prime_config(self, argv, config_files):
        config_files = config_files or []
        for config_file in config_files:
            self._config.grab_from_file(config_file)
        self._config.grab_from_env()
        self._config.grab_from_argv(argv[1:])

    def main(self, argv=list(sys.argv), env=os.environ.copy(), config_files=None):
        return self.execute(argv, env, config_files)


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



