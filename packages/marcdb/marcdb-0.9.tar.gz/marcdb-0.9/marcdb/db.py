from elixir import *

"""
a very slim wrapper around some elixir functions
to connect to, create, commit to and clean a marcdb
"""

def connect(uri):
  metadata.bind = uri

def create():
  setup_all()
  create_all()

def commit():
  session.flush()
  session.clear()

def zap():
  drop_all()
  objectstore.clear()
