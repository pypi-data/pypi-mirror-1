
import os, sys

import yaml

from jinja2 import Environment
from jinja2.loaders import BaseLoader
from jinja2.exceptions import TemplateNotFound

from sanescript import Command, Option, processors

class JinjaYamlLoader(BaseLoader):

    def __init__(self, path):
        self.path = path
        f = open(self.path, 'r')
        self.templates = yaml.load(f)
        f.close()

    def get_source(self, environment, name):
        try:
            return self.templates[name], name, lambda: False
        except KeyError:
            raise TemplateNotFound(name)


class TemplateCommand(Command):

    template_file = None
    target = None

    exclude_interactive = ['template_file', 'target']

    base_options = [
        Option('template_file', help='The template file.', short_name='f'),
        Option('target', help='The target in the template file to build.'),
        Option('output_directory', help='Output directory',
                default=os.path.abspath(os.getcwd()),
                processor=os.path.abspath),
    ]

    options = [] + base_options

    def _create_env(self, config):
        self.loader = JinjaYamlLoader(config.template_file or self.template_file)
        self.env = Environment(loader=self.loader)
        self.targets = self.loader.templates.get('__targets__')
        target_name = config.target or self.target
        if target_name is None:
            target_name = self.targets.keys()[0]
        self.target = self.targets.get(target_name)

    def __call__(self, config):
        self._create_env(config)
        for k, v in self.target.items():
            self._visit_target(config, k, v, config.output_directory)

    def _visit_target(self, config, k, v, p):
        # the name could be a template
        name = self.env.from_string(k).render(config.to_dict())
        path = os.path.join(p, name)
        if isinstance(v, dict):
            os.mkdir(path)
            for k, v in v.items():
                self._visit_target(config, k, v, path)
        else:
            if isinstance(v, list):
                template_name, options = v
            else:
                template_name = v
                options = {}
            f = open(path, 'w')
            t = self.env.get_template(template_name)
            f.write(t.render(config.to_dict()))
            f.close()

python_entities_template_file = os.path.join(os.path.dirname(__file__),
                                             'python_entities.yml')

class ProjectTemplateCommand(TemplateCommand):

    name = 'project'

    options = TemplateCommand.base_options + [
        Option('package', help='The package name', short_name='p'),
        Option('project', help='The project name', short_name='n'),
        Option('version', help='Initial project version',
                short_name='V'),
        Option('encoding', help='Source code encoding',
                short_name='e', default='utf-8'),
        Option('description', help='Project description')
    ]

    template_file = python_entities_template_file
    target = 'project'

    include_interactive = ['project', 'version', 'package', 'encoding',
                           'description']


class PackageTemplateCommand(TemplateCommand):

    name = 'package'

    options = TemplateCommand.base_options + [
        Option('package', help='The package name', short_name='p'),
        Option('encoding', help='Source code encoding',
                short_name='e', default='utf-8'),
        Option('description', help='Project description')
    ]

    template_file = python_entities_template_file
    target = 'package'

    include_interactive = ['package', 'encoding', 'description']


if __name__ == '__main__':
    from sanescript import register, main
    register(PackageTemplateCommand)
    register(ProjectTemplateCommand)
    main()

