from unittest import TestCase
from marcdb import db

class DatabaseTest(TestCase):
  """
  Each test gets it's own clean database
  """

  def setUp(self):
    db.connect('sqlite:///test/marc.db')
    db.create()

  def tearDown(self):
    db.zap()
