from os import path
from ConfigParser import SafeConfigParser, ParsingError

class Config:

  def __init__(self, config_file=''):
    try:
      parser = SafeConfigParser()
      parser.read([config_file, path.expanduser('~/.marcdb')])
      self.config = parser
    except ParsingError, e:
      print "unable to read marcdb configuration: %s" % str(e)

  def get(self, section, option):
    return self.config.get(section, option)
