from marcdb.loader import Loader
from marcdb.db import connect
from marcdb.models import Record
from database_test import DatabaseTest

class LoadTest(DatabaseTest):

  def test_load(self):
    loader = Loader('sqlite:///test/marc.db')
    loader.load('test/batch.dat')
    records = Record.select()
    self.assertEqual(len(records), 10)

  def test_load_xml(self):
    """
    test that we can load xml into the db
    """

    loader = Loader('sqlite:///test/marc.db')
    loader.load_xml('test/batch.xml')

    records = Record.select()
    self.assertEqual(len(records), 2)

    r = records[0]

    # check a control field
    control_fields = r.control_fields
    self.assertEqual(len(control_fields), 5)
    cf = control_fields[0]
    self.assertEqual(cf.tag, '001')
    self.assertEqual(cf.value, '5637241')
    self.assertEqual(cf.position, 0)

    # check a data field
    data_fields = r.data_fields
    self.assertEqual(len(data_fields), 13)
    df = data_fields[4]
    self.assertEqual(df.tag, '245')
    self.assertEqual(df.indicator1, '0')
    self.assertEqual(df.indicator2, '4')

    # check the subfields of a data field
    subfields = df.subfields
    self.assertEqual(len(subfields), 2)
    self.assertEqual(subfields[0].position, 0)
    self.assertEqual(subfields[0].code, 'a')
    self.assertEqual(subfields[0].value, 'The Great Ray Charles')
    self.assertEqual(subfields[1].position, 1)
    self.assertEqual(subfields[1].code, 'h')
    self.assertEqual(subfields[1].value, '[sound recording].')



