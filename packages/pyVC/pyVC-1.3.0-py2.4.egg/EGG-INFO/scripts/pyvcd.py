#!/usr/bin/python2.4
from sys import argv, exit
from time import sleep
from pyVC.RemoteMachine import RemoteMachine
from pyVC.pyVCd import pyVCdData
from optparse import OptionParser, OptionGroup

import Pyro.core
import os
import socket

object = "pyvcd"

WORKDIR = "/tmp"
UMASK = 0
REDIRECT = os.devnull

usage = """usage: pyvcd.py [options]
       pyvcd.py [options] -H hostname -p port"""
opt = OptionParser(usage=usage)
opt.add_option( '-H', '--hostname', action='store', \
                dest='hostname', type='string', default=None, \
                help='pyvcd hostname or IP to connect to' )
opt.add_option( '-p', '--port', action='store', \
                dest='port', type='string', default='7766', \
                help='pyvcd port number to connect to' )
opt.add_option( '-D', '--debug', action='store_true', \
                dest='debug', \
                help='enable debug options' )
opt.add_option( '-d', '--daemon', action='store_true', \
                dest='daemon', \
                help='run as a daemon' )
opt.add_option( '-l', '--logfile', action='store', \
                dest='logfile', \
                help='logfile to write log to when running as a daemon' )
opt.add_option( '-P', '--pidfile', action='store', \
                dest='pidfile', \
                help='pidfile to store pid in when running as a daemon' )
opt.add_option( '-b', '--bind-address', action='store', \
                dest='bind_address', default="", \
                help='address to bind server to' )
opt.add_option( '-s', '--server-port', action='store', \
                dest='server_port', type='int', default=7766, \
                help='port for server to listen on' )
(options, args) = opt.parse_args()


if options.debug:
    Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

def start_daemon(serverip, serverport):
    os.chdir(WORKDIR)
    os.umask(UMASK)
    Pyro.core.initServer(banner=0, storageCheck=0)
    try:
        daemon = Pyro.core.Daemon(host=serverip, port=serverport)
    except socket.error, e:
        print "ERROR: please use -b to specify IP address to bind to"
        exit(0)

    return daemon

try:
    machine = RemoteMachine()
except ValueError, e:
    print e
    exit(0)

if not options.hostname:
    pyvcd = pyVCdData()
    pyvcd.add_machine(machine)

    daemon = start_daemon(options.bind_address, options.server_port)
    
    uri = daemon.connect(pyvcd, "pyvcd")

    print "Server running at %s" % (uri)

else:
    Pyro.core.initClient(0)
    uri = "PYROLOC://%s:%s/%s" % (options.hostname, options.port, "pyvcd")
    pyvcd = Pyro.core.getAttrProxyForURI(uri)
    pyvcd._setOneway('add_machine')

    daemon = start_daemon(options.bind_address, options.server_port)

    uri = daemon.connect(machine, "machine")

    if machine.hostname not in pyvcd.machinenames:
        try:
            pyvcd.add_machine(uri)
        except Pyro.errors.ProtocolError, e:
            print "ERROR: Pyro returned \"%s\"." % e
            exit(-1)
    else:
        print "ERROR: %s already exists in pyvcd." % machine.hostname
        exit(-1)

if options.daemon:
    try:
        pid = os.fork()
    except OSError, e:
        raise Exception, "%s [%d]" % (e.strerror, e.errno)
    if (pid == 0):
        os.setsid()
        try:
            pid = os.fork()
        except OSError, e:
            raise Exception, "%s [%d]" % (e.strerror, e.errno)

        if (pid == 0):
            os.chdir(WORKDIR)
            os.umask(UMASK)
            daemon.requestLoop()
        else:
            try:
                pidfd = open(options.pidfile, 'w')
                pidfd.write("%s\n" % (pid))
                pidfd.close()
            except:
                pass
            os._exit(0)
    else:
        os._exit(0)
        
    import resource
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD
  
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:
            pass

    os.open(REDIRECT, os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)
    
else:
    print "Press CTRL-C to exit"
    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        pass

if options.hostname:
    pyvcd.del_machine(machine.hostname)
