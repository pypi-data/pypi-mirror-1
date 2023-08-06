from setuptools import setup

import sanescript

setup(
    name = 'Sanescript',
    description = sanescript.__doc__,
    version = 0.3,
    author='Ali Afshar',
    author_email='aafshar@gmail.com',
    py_modules = ['sanescript'],
    install_requires = ['pyyaml', 'argparse'],
)

