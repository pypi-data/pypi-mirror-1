#!/usr/bin/python2.4

from pyVC import Config

config = Config()

precedence = 0
for file in config.configfiles:
  print "%s read from %s" % (precedence, file)
  precedence += 1

for heading,entries in config.items():
  print "[%s]" % heading
  for key,value in entries.items():
    print "%s=%s" % (key, value)
