# -*- coding: utf-8 -*-

"""
    sanescript.processing
    ~~~~~~~~~~~~~~~~~~~~~

    Ways to mutate options into useful things.

    :copyright: 2009-2010 Ali Afshar <aafshar@gmail.com>
    :license: MIT
"""

import os


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

