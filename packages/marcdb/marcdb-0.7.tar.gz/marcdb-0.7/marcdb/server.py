#!/usr/bin/env python

from marcdb.models import Record, ControlField
from marcdb.db import connect
from marcdb.xml import record2xml

import web
import sys

urls = (
  '/(.*)', 'RecordHandler'
)

class RecordHandler:

  def GET(self, identifier):
    field = ControlField.get_by(tag='001', value=identifier)
    if field:
      record = field.record
      web.header('Content-type', 'text/xml')
      print record2xml(record)

def run_server(db_uri):
  connect(db_uri)
  # TODO: invoke web.py correctly instead of using run which looks for
  # the port to use in argv
  sys.argv = []
  web.run(urls, globals())
