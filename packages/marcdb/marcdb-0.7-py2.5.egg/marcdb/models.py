from elixir import *
from sqlalchemy import desc
from datetime import datetime
import pymarc

class ControlField(Entity):
  has_field('tag', Unicode)
  has_field('position', Integer)
  belongs_to('record', of_kind='Record')
  has_field('value', Unicode)
  using_options(tablename='control_fields')

class Record(Entity):
  has_field('leader', Unicode)
  has_field('created', DateTime, default=datetime.now)
  has_many('control_fields', of_kind='ControlField', order_by='position')
  has_many('data_fields', of_kind='DataField', order_by='position')
  using_options(tablename='records')

  def to_marc(self):
    r = pymarc.Record()
    r.leader
    for cf in self.control_fields:
      r.addField(pymarc.Field(tag=cf.tag, data=cf.value))
    for df in self.data_fields:
      f = pymarc.Field(tag=df.tag, indicators=[df.indicator1, df.indicator2])
      for sf in df.subfields:
        f.addSubfield(sf.code, sf.value)
      r.addField(f)
    return r.asMARC21()

class DataField(Entity):
  has_field('tag', Unicode)
  has_field('indicator1', String(length=1))
  has_field('indicator2', String(length=1))
  has_field('position', Integer)
  belongs_to('record', of_kind='Record')
  has_many('subfields', of_kind='Subfield', order_by='position')
  using_options(tablename='data_fields')

  def __str__(self):
    s = "%s %s%s " % (self.tag, self.indicator1, self.indicator2)
    for sf in self.subfields:
      s += '$' + sf.code + sf.value
    return s


class Subfield(Entity):
  has_field('code', String(length=1))
  has_field('value', Unicode)
  has_field('position', Integer)
  belongs_to('data_field', of_kind='DataField')
  using_options(tablename='subfields')

