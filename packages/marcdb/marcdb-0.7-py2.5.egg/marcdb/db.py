from elixir import *

"""
a very slim wrapper around some elixir functions
to connect to, create, commit to and clean a marcdb
"""

def connect(uri):
  metadata.connect(uri)

def create():
  create_all()

def commit():
  objectstore.flush()

def zap():
  drop_all()
  objectstore.clear()

