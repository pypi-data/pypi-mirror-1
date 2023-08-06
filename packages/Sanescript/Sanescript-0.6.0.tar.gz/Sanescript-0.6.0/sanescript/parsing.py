# -*- coding: utf-8 -*-

"""
    sanescript.parsing
    ~~~~~~~~~~~~~~~~~~

    Slightly more pleasant interface to argparse than juggling the 2 + n
    number of parsers required by argparse to allow sanescript to behave
    correctly with regards config files and control flow.

    :copyright: 2009-2010 Ali Afshar <aafshar@gmail.com>
    :license: MIT
"""

from argparse import ArgumentParser

from config import UNSET


class Parser(object):
    """Argument parser interface
    """

    def __init__(self, pre_options=None):
        self._pre_parser = ArgumentParser(add_help=False)
        if pre_options is not None:
            for opt in pre_options:
                self.add_option(opt, self._pre_parser)
        self._parser = ArgumentParser(parents=[self._pre_parser])
        self._subparser_factory = None
        self._command_parsers = {}

    def add_option(self, opt, parser=None, prefix=None):
        if prefix:
            parser = self._command_parsers[prefix]
        else:
            parser = parser or self._parser
        kw = opt.optparse_kw.copy()
        if opt.converter:
            kw['type'] = opt.converter
        add_arg = parser.add_argument
        if opt.positional:
            add_arg(opt.name, help=opt.help, default=UNSET, **kw)
        else:
            add_arg(opt.short_opt, opt.long_opt, help=opt.help, default=UNSET,
                    required=opt.required, **kw)

    def add_command(self, command):
        if self._subparser_factory is None:
            self._subparser_factory = self._parser.add_subparsers(
                dest='__command__')
        parser = self._subparser_factory.add_parser(command.name, help=command.__doc__)
        self._command_parsers[command.name] = parser

    def pre_parse(self, argv):
        args, remainder = self._pre_parser.parse_known_args(argv)
        return args

    def parse(self, argv):
        return self._parser.parse_args(argv)

    def update(self, values):
        self._parser.set_defaults(**values)

