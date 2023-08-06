def help(opts):
  if len(opts) == 0:
    topic = None
  else:
    topic = opts[0]

  if topic == None:
    print detailed_usage
  elif topic == 'create':
    print create_usage
  elif topic == 'load':
    print load_usage
  elif topic == 'load-xml':
    print load_xml_usage
  elif topic == 'server':
    print server_usage
  exit(1)

general_usage = """
Type 'marcdb help' for usage.
"""

detailed_usage = """
Type 'marcdb help <subcommand>' for help on a specific subcommand.

Available subcommands:
  create
  load
  load-xml
"""

create_usage = """
create: create a marcdb given a particular database URI
usage: create sqlite:///example.db
"""

load_usage = """
load: load a MARC file into a given marcdb instance
usage: load marc.dat sqlite:///example.db
"""

load_xml_usage = """
load-xml: load a marcxml file into a given marcdb instance
usage: load-xml marc.xml sqlite:///example.db 
"""

server_usage = """
server: start a http server on port 8080 to serve up records
usage: server sqlite://example.db
"""
