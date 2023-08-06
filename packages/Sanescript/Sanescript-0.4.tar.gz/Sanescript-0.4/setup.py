
from setuptools import setup, find_packages

"""
"""

setup(
    name = 'Sanescript',
    description = __doc__,
    version = 0.4,
    author='Ali Afshar',
    author_email='aafshar@gmail.com',
    packages = ['sanescript'],
    install_requires = ['pyyaml', 'argparse'],
)

