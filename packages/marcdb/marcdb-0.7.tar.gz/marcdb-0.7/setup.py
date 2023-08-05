import os

from setuptools import setup
setup(
  name = 'marcdb',
  version = '0.7',
  author = 'Ed Summers',
  author_email = 'ehs@pobox.com',
  description = 'parse MARC data and store into a rdbms',
  packages = ['marcdb'],
  test_suite = 'test',
  install_requires = ['sqlalchemy', 'elixir', 'pymarc >= 1.2', 'elementtree', 
    'web.py'],
  scripts = ['scripts/marcdb']
)

