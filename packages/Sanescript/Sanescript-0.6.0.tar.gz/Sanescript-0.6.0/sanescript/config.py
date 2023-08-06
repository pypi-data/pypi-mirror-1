# -*- coding: utf-8 -*-

"""
    sanescript.config
    ~~~~~~~~~~~~~~~~~

    Define option schemas, and read config data from a number of sources.

    :copyright: 2009-2010 Ali Afshar <aafshar@gmail.com>
    :license: MIT
"""

import os


class Unset(object):
    """Perform the task of marking an unset state
    """

    def __nonzero__(self):
        return False

    def __str__(self):
        return '<UNSET>'

# We must have an UNSET state to differentiate from native types which provide
# a None equivalent as valid data
UNSET = Unset()


class Option(object):
    """An option definition.

    This should be declared before creating the Config instance and is used to
    tell the config how to manage the options it finds.

    :param name: a unique option name.
    :param help: a help text or description for the option.
    :param default: the default value
    :param short_name: a single letter representing the short name for short
                       options. If omitted will use the first letter of the
                       name parameter.
    :param converter: a Python callable to pass the value into to convert to a
                      useful Python value.
    :param processor: a Python callable used to process the data. This is
                      distinct from the converter, because processors are
                      applied to native types not needing conversion
    :param argparse_kw: additional keyword arguments to pass to the argparse
                        add_arg call.
    :param positional: flag as to whether the argument is positional or not

    >>> o = Option('test', 'this is a test option', 'default')
    >>> o.long_opt
    '--test'
    >>> o.short_opt
    '-t'
    """

    def __init__(self, name, help=None, default=UNSET, short_name=None, converter=None,
                       processor=None, required=False, positional=False, **optparse_kw):
        self.name = name
        if short_name is None:
            short_name = self.name[0]
        self.short_name = short_name
        self.help = help
        self.default = default
        self.converter = converter
        self.processor = processor
        self.required = required
        self.positional = positional
        self.optparse_kw = optparse_kw

    @property
    def long_opt(self):
        return '--%s' % self.name

    @property
    def short_opt(self):
        return '-%s' % self.short_name


class Config(object):
    """The configuration instance.

    This has the values set as attributes on itself.
    """
    def __init__(self, parser=None, env_prefix=None):
        self._env_prefix = env_prefix
        self._parser = parser
        self._options = {}

    def add_option(self, opt, prefix=None):
        """Add an option declaration.

        :param opt: an Option instance.
        """
        self._options[opt.name, prefix] = opt
        if prefix != "__pre__" and self._parser:
            self._parser.add_option(opt, prefix=prefix)
        setattr(self, opt.name, opt.default)

    def add_options(self, options, prefix=None):
        """Add a number of options.
        """
        for option in options:
            self.add_option(option, prefix)

    def grab_from_env(self, env=None):
        """Search the env dict for overriden values.

        This will employ the env_prefix, or if not set just capitalize the name
        of the variables.

        :param env: is an optional dict, if omitted, os.environ will be used.
        """
        if env is None:
            env = os.environ
        for (name, prefix), opt in self._options.items():
            env_name = name.upper()
            if prefix:
                env_name = '%s_%s' % (prefix.upper(), env_name)
            if self._env_prefix:
                env_name = '%s_%s' % (self._env_prefix, env_name)
            raw = env.get(env_name)
            if raw is None:
                continue

            val = raw
            if opt.converter is not None:
                val = opt.converter(val)
            if opt.processor is not None:
                val = opt.processor(val)
            setattr(self, name, val)

    def grab_from_file(self, path):
        """Get values from an ini config file.
        """
        file = ConfigFile(path)
        for (name, prefix), opt in self._options.items():
            val = file.get(name, prefix)
            if val is not UNSET:
                if opt.processor is not None:
                    val = opt.processor(val)
                setattr(self, name, val)

    def grab_from_argv(self, argv):
        """Get values from argv list
        """
        args = self._parser.parse(argv)
        self.grab_from_ns(args)
        try:
            self.__command__ = args.__command__
        except AttributeError:
            self.__command__ = None

    def grab_from_ns(self, ns):
        for (name, prefix), opt in self._options.items():
            try:
                val = getattr(ns, name)
                if val is UNSET:
                    continue
            except AttributeError:
                continue
            if opt.processor is not None:
                val = opt.processor(val)
            setattr(self, name, val)

    def grab_from_dict(self, d):
        """Load the options from a dict.

        This is useful if you want to dump or import options say as json.
        """
        for k, v in d.items():
            setattr(self, k, v)

    def items(self):
        for (name, prefix) in self._options:
            yield name, getattr(self, name)

    def to_dict(self):
        """Serialize the options to a dict.

        This is useful if you want to dump or import options say as json.
        """
        return dict(self.items())

    def pregrab_from_argv(self, argv):
        """Internal Sanescript API to pregrab some vital information from
           argparse before parsing the entire command line.
        """
        args = self._parser.pre_parse(argv)
        self.grab_from_ns(args)


class ConfigFile(object):
    """A YAML configuration file.
    """

    def __init__(self, filename):
        import yaml
        f = open(filename)
        self._values = yaml.load(f)
        f.close()

    def get(self, name, prefix):
        if prefix is None:
            master = self._values
        else:
            master = self._values.get(prefix)
        if master is not None:
            return master.get(name)
        else:
            return UNSET

