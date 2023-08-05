#!/usr/bin/env python2.4

from lxml.etree import XML, XMLSchema, parse, XMLSyntaxError, XMLSchemaParseError
from pkg_resources import resource_string
from sys import argv, exit
from pyVC import Config

if len(argv) <= 1:
  print "USAGE: %s file1.xml file2.xml ..." % argv[0]
  exit(-1)

config = Config()

if 'vcml_schema' not in config['pyvc']:
  print "ERROR: schema path not in pyVC.ini"

try:
  schematext = resource_string('pyVC', 'vcml.xsd')
  schemafile = XML( schematext )
except IOError:
  print "ERROR: could not open schema file %s." % config['pyvc']['vcml_schema']
  exit(-1)
except XMLSyntaxError, e:
  print "ERROR: schema file contains XML syntax error."
  print e
  exit(-1)

try:
  schema = XMLSchema(schemafile)
except XMLSchemaParseError, e:
  print "ERROR: schema file contains XML schema syntax error."
  print e.error_log
  exit(-1)

for file in argv[1:]:
  try:
    configfile = parse(file)
  except IOError:
    print "ERROR: could not open file %s." % file
    configfile = None
  except XMLSyntaxError, e:
    print "ERROR: file %s contains XML syntax error." % file
    print e
    configfile = None

  if configfile:
    rc = None
    try:
      rc = schema(configfile)
    except TypeError:
      rc = schema.validate(configfile)
    if not rc:
      print "ERROR: file %s does not validate with schema." % file
      print schema.error_log.__repr__()
