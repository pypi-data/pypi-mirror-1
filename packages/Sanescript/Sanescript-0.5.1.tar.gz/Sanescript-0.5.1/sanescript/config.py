
import sys, os

from argparse import ArgumentParser


class _OptionProcessors(object):
    """Some common processors
    """
    def python_import(self, import_name):
        """Import a python string
        """
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        return getattr(__import__(module, None, None, [obj]), obj)

    def file(self, mode='r'):
        def _file(file_name, mode=mode):
            return open(file_name, mode)
        return _file

    def virtualenv(self, path):
        path = os.path.abspath(path)
        activator = os.path.join(path, 'bin', 'activate_this.py')
        execfile(activator, dict(__file__ = activator))

processors = _OptionProcessors()


class Unset(object):
    """Perform the task of marking an unset state
    """

    def __nonzero__(self):
        return False

    def __str__(self):
        return '<UNSET>'

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
    :param argparse_kw: additional keyword arguments to pass to the argparse
                        add_arg call.

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
        self._parser = parser or ArgumentParser() # we don't always get passed
                                                  # a parser because we may be
                                                  # running independently of
                                                  # the scripting framework.
        self._options = {}

    def add_option(self, opt, prefix=None, parser=None):
        """Add an option declaration.

        :param opt: an Option instance.
        """
        self._options[opt.name, prefix] = opt
        parser = parser or self._parser
        kw = opt.optparse_kw.copy()
        if opt.converter:
            kw['type'] = opt.converter
        if opt.positional:
            parser.add_argument(opt.name,
                                help=opt.help, default=UNSET,
                                **kw)
        else:
            parser.add_argument(opt.short_opt, opt.long_opt,
                                help=opt.help, default=UNSET,
                                **kw)
        setattr(self, opt.name, opt.default)

    def add_options(self, options, prefix=None, parser=None):
        """Add a number of options.
        """
        for option in options:
            self.add_option(option, prefix, parser)

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
        args = self._parser.parse_args(argv)

        for (name, prefix), opt in self._options.items():
            try:
                val = getattr(args, name)
                if val is UNSET:
                    continue
            except AttributeError:
                continue
            if opt.processor is not None:
                val = opt.processor(val)
            setattr(self, name, val)
        try:
            self.__command__ = args.__command__
        except AttributeError:
            self.__command__ = None

    def grab_from_dict(self, d):
        """Load the options from a dict.

        This is useful if you want to dump or import options say as json.
        """
        for k, v in d.items():
            setattr(self, k, v)

    def grab_from_interactive(self, prefix, include, exclude):
        if not include:
            include = [n for (n, p) in self._options.keys()]
        for name in include:
            if name in exclude:
                continue
            opt = self._options.get((name, prefix))
            if opt is None:
                continue
            from utils import do_prompt
            raw = do_prompt(name, opt.help, opt.default or UNSET)
            val = raw.strip()
            if opt.converter:
                val = opt.converter(val)
            if opt.processor:
                val = opt.processor(val)
            setattr(self, name, val)

    def items(self):
        for (name, prefix) in self._options:
            yield name, getattr(self, name)

    def to_dict(self):
        """Serialize the options to a dict.

        This is useful if you want to dump or import options say as json.
        """
        return dict(self.items())

    def ensure_required(self):
        for (name, prefix), option in self._options.items():
            if prefix != self.__command__:
                continue
            if option.required and getattr(self, option.name) is UNSET:
                print 'Error: "%s" is required.' % option.name
                print
                print 'It could be provided as:'
                print
                print '\t-%s --%s on the command line,' % (option.short_name, option.name)
                if prefix:
                    print '\t%s_%s' % (prefix.upper(), name.upper()), 'in the environment'
                else:
                    print name, 'in the environment'
                print '\tOr in any config files'
                print
                return False
        return True


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

