import os
import sys

from setuptools import setup
setup(
  name = 'marcdb',
  version = '0.92', # keep in sync w/ marcdb/__init__.py
  author = 'Ed Summers',
  author_email = 'ehs@pobox.com',
  url = 'http://inkdroid.org/bzr/marcdb',
  description = 'parse MARC data and store into a rdbms',
  packages = ['marcdb'],
  test_suite = 'test',
  install_requires = ['elixir >= 0.5.1', 'pymarc >= 2.0', 'elementtree', 'web.py'],
  scripts = ['scripts/marcdb']
)

