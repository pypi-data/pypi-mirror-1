from marcdb.loader import Loader
from marcdb.models import DataField
from database_test import DatabaseTest

class LoadTest(DatabaseTest):

  def setUp(self):
    DatabaseTest.setUp(self)
    loader = Loader('sqlite:///test/marc.db')
    loader.load('test/batch.dat')

  def test_query(self):
    fields = DataField.select_by(tag='245')
    self.assertEqual(str(fields[1]), '245 10 $aProgramming the Perl DBI /$cAlligator Descartes and Tim Bunce.')
    self.assertEqual(str(fields[9]), '245 10 $aCross-platform Perl /$cEric F. Johnson.')

