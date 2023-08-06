
from setuptools import setup, find_packages

"""
"""

setup(
    name = 'Sanescript',
    description = __doc__,
    version = '0.4.1',
    author='Ali Afshar',
    author_email='aafshar@gmail.com',
    packages = ['sanescript', 'sanescript.ext'],
    install_requires = ['pyyaml', 'argparse'],
)

