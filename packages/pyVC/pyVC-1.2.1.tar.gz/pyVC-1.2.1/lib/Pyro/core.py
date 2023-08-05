#############################################################################
#  
#	$Id: core.py,v 2.68 2004/05/10 20:30:37 irmen Exp $
#	Pyro Core Library
#
#	This is part of "Pyro" - Python Remote Objects
#	which is (c) Irmen de Jong - irmen@users.sourceforge.net
#
#############################################################################

import sys, time, sre, traceback, os
import Pyro
import util, protocol, constants
from errors import *
from types import UnboundMethodType, MethodType, BuiltinMethodType, TupleType, StringType, UnicodeType

Log=util.Log


def _checkInit(pyrotype="client"):
	if not getattr(Pyro.config, constants.CFGITEM_PYRO_INITIALIZED):
		# If Pyro has not been initialized explicitly, do it automatically.
		if pyrotype=="server":
			initServer()
		else:
			initClient()


#############################################################################
#
#	ObjBase		- Server-side object implementation base class
#	              or master class with the actual object as delegate
#
#	SynchronizedObjBase - Just the same, but with synchronized method
#                         calls (thread-safe).
#
#############################################################################

class ObjBase:
	def __init__(self):
		self.objectGUID=util.getGUID()
		self.delegate=None
		self.lastUsed=time.time()		# for later reaping unused objects
		if Pyro.config.PYRO_MOBILE_CODE:
			self.codeValidator=lambda n,m,a: 1  # always accept
	def GUID(self):
		return self.objectGUID
	def setGUID(self, guid):			# used with persistent name server
		self.objectGUID = guid
	def delegateTo(self,delegate):
		self.delegate=delegate
	def setDaemon(self, daemon):
		# This will usually introduce a cyclic reference between the
		# object and the daemon. Use a weak ref if available.
		# NOTE: if you correctly clean up the object (that is, disconnect it from the daemon)
        # the cyclic reference is cleared correctly, and no problem occurs.
		# NOTE: you have to make sure your original daemon object doesn't get garbage collected
		# if you still want to use the objects! You have to keep a ref. to the daemon somewhere.
		self.daemon=util.weakref(daemon)
	def setCodeValidator(self, v):
		if not callable(v):
			raise TypeError("codevalidator must be a callable object")
		self.codeValidator=v
	def getDaemon(self):
		return self.daemon
	def getLocalStorage(self):
		return self.daemon.getLocalStorage()
	def _gotReaped(self):
		# Called when daemon reaps this object due to unaccessed time
		# Override this method if needed; to act on this event
		pass
	def getProxy(self):
		return self.daemon.getProxyForObj(self)
	def getAttrProxy(self):
		return self.daemon.getAttrProxyForObj(self)
	def Pyro_dyncall(self, method, flags, args):
		# update the timestamp
		self.lastUsed=time.time()
		# find the method in this object, and call it with the supplied args.
		keywords={}
		if flags & constants.RIF_Keywords:
			# reconstruct the varargs from a tuple like
			#  (a,b,(va1,va2,va3...),{kw1:?,...})
			keywords=args[-1]
			args=args[:-1]
		if flags & constants.RIF_Varargs:
			# reconstruct the varargs from a tuple like (a,b,(va1,va2,va3...))
			args=args[:-1]+args[-1]
		# If the method is part of ObjBase, never call the delegate object because
		# that object doesn't implement that method. If you don't check this,
		# remote attributes won't work with delegates for instance, because the
		# delegate object doesn't implement _r_xa. (remote_xxxattr)
		if method in dir(ObjBase):
			return getattr(self,method) (*args,**keywords)
		else:
			# try..except to deal with obsoleted string exceptions (raise "blahblah")
			try :
				return getattr(self.delegate or self,method) (*args,**keywords)
			except :
				exc_info = sys.exc_info()
				if type(exc_info[0]) == StringType :
					if exc_info[1] == None :
						raise Exception, exc_info[0], exc_info[2]
					else :
						raise Exception, "%s: %s" % (exc_info[0], exc_info[1]), exc_info[2]
				else :
					raise
	# remote getattr/setattr support:
	def _r_ha(self, attr):
		try:
			attr = getattr(self.delegate or self,attr)
			if type(attr) in (UnboundMethodType, MethodType, BuiltinMethodType):
				return 1 # method
		except:
			pass
		return 2 # attribute
	def _r_ga(self, attr):
		return getattr(self.delegate or self, attr)
	def _r_sa(self, attr, value):
		setattr(self.delegate or self, attr, value)
	# remote code downloading support (server downloads from client):
	def remote_supply_code(self, name, module, sourceaddr):
		if Pyro.config.PYRO_MOBILE_CODE and self.codeValidator(name,module,sourceaddr):
			import imp,marshal,new
			Log.msg('ObjBase','loading supplied code: ',name,'from',str(sourceaddr))
			name=name.split('.')
			# make the module hierarchy and add all names to sys.modules
			path=''
			mod=new.module("pyro-agent-context")

			for m in name:
				path+='.'+m
				# use already loaded modules instead of overwriting them
				real_path = path[1:]
				if sys.modules.has_key(real_path):
					mod = sys.modules[real_path]
				else:
					setattr(mod,m,new.module(path[1:]))
					mod=getattr(mod,m)
					sys.modules[path[1:]]=mod
				
			if module[0:4]!=imp.get_magic():
				# compile source code
				code=compile(module,'<downloaded>','exec')
			else:
				# read bytecode from the client
				code=marshal.loads(module[8:])
			# finally, execute the module code in the right module.	A
			exec code in mod.__dict__
		else:
			Log.warn('ObjBase','attempt to supply code denied: ',name,'from',str(sourceaddr))
			raise PyroError('attempt to supply code denied')

	# remote code retrieve support (client retrieves from server):
	def remote_retrieve_code(self, name):
		# XXX codeValidator: can we somehow get the client's address it is sent to?
		if Pyro.config.PYRO_MOBILE_CODE and self.codeValidator(name,None,None):
			Log.msg("ObjBase","supplying code: ",name)
			import new
			try:
				importmodule=new.module("pyro-server-import")
				try:
					exec "import " + name in importmodule.__dict__
				except ImportError:
					Log.error("ObjBase","Client wanted a non-existing module:", name)
					raise PyroError("Client wanted a non-existing module", name)
				m=eval("importmodule."+name)
				# try to load the module's compiled source, or the real .py source if that fails.
				(filebase,ext)=os.path.splitext(m.__file__)
				if ext.startswith(".PY"):
					exts = ( ".PYO", ".PYC", ".PY" )	# uppercase
				else:
					exts = ( ".pyo", ".pyc", ".py" )	# lowercase
				for ext in exts:
					try:
						m=open(filebase+ext, "rb").read()
						return m  # supply the module to the client!
					except:
						pass
				Log.error("ObjBase","cannot read module source code for module:", name)
				raise PyroError("cannot read module source code")
			finally:
				del importmodule
		else:
			Log.error("ObjBase","attempt to retrieve code denied:", name)
			raise PyroError("attempt to retrieve code denied")


class SynchronizedObjBase(ObjBase):
	def __init__(self):
		ObjBase.__init__(self)
		# synchronized method invocations
		self.synlock=util.getLockObject()
	def Pyro_dyncall(self, method, flags, args):
		# (this looks very much the same as Objbase's implementation)
		# update the timestamp
		self.lastUsed=time.time()
		# find the method in this object, and call it with the supplied args.
		keywords={}
		if flags & constants.RIF_Keywords:
			# reconstruct the varargs from a tuple like
			#  (a,b,(va1,va2,va3...),{kw1:?,...})
			keywords=args[-1]
			args=args[:-1]
		if flags & constants.RIF_Varargs:
			# reconstruct the varargs from a tuple like (a,b,(va1,va2,va3...))
			args=args[:-1]+args[-1]
		# synchronize method invocation
		self.synlock.acquire()
		try:
			# If the method is part of ObjBase, never call the delegate object because
			# that object doesn't implement that method. If you don't check this,
			# remote attributes won't work with delegates for instance, because the
			# delegate object doesn't implement _r_xa. (remote_xxxattr)
			if method in dir(ObjBase):
				return getattr(self,method) (*args,**keywords)
			else:
				return getattr(self.delegate or self,method) (*args,**keywords)
		finally:
			self.synlock.release()


# Use this class instead if you're using callback objects and you
# want to see local exceptions. (otherwise they go back to the calling server...)
class CallbackObjBase(ObjBase):
	def __init__(self):
		ObjBase.__init__(self)
	def Pyro_dyncall(self, method, flags, args):
		try:
			return ObjBase.Pyro_dyncall(self,method,flags,args)
		except Exception,x:
			# catch all errors
			Log.warn('CallbackObjBase','Exception in callback object: ',x)
			raise PyroExceptionCapsule(x,str(x))


#############################################################################
#
#	PyroURI		- Pyro Universal Resource Identifier
#
#	This class represents a Pyro URI (which consists of four parts,
#	a protocol identifier, an IP address, a portnumber, and an object ID.
#	
#	The URI can be converted to a string representation (str converter).
#	The URI can also be read back from such a string (reinitFromString).
#	The URI can be initialised from its parts (init).
#	The URI can be initialised from a string directly, if the init
#	 code detects a ':' and '/' in the host argument (which is then
#        assumed to be a string URI, not a host name/ IP address).
#
#############################################################################

class PyroURI:
	def __init__(self,host,objectID=0,port=0,prtcol='PYRO'):
		# if the 'host' arg is a PyroURI, copy contents
		if isinstance(host, PyroURI):
			self.reinitFromString(str(host))
		else:
			# If the 'host' arg contains '://', assume it's an URI string.
			if host.find('://')>0:
				self.reinitFromString(host)
			else:
				if '/' in host:
					raise URIError('malformed hostname')
				if Pyro.config.PYRO_DNS_URI:
					self.address = host
				else:
					self.address=protocol.getIPAddress(host)
					if not self.address:
						raise URIError('unknown host')
				if port:
					if type(port)==type(1):
						self.port=port
					else:
						raise TypeError("port must be integer")
				else:
					self.port=Pyro.config.PYRO_PORT
				self.protocol=prtcol
				self.objectID=objectID
	def __str__(self):
		return self.protocol+'://'+self.address+':'+str(self.port)+'/'+self.objectID
	def __repr__(self):
		return '<PyroURI \''+str(self)+'\'>'
	def __hash__(self):
		# XXX this is handy but not safe. If the URI changes, the object will be in the wrong hash bucket.
		return hash(str(self))
	def __cmp__(self, o):
		return cmp(str(self), str(o))
	def clone(self):
		return PyroURI(self)
	def init(self,address,objectID,port=0,prtcol='PYRO'):
		self.address=address
		self.objectID=objectID
		if port:
			self.port=port
		else:
			self.port=Pyro.config.PYRO_PORT
		self.protocol=prtcol
	def reinitFromString(self,arg):
		if arg.startswith('PYROLOC') or arg.startswith('PYRONAME'):
			uri=processStringURI(arg)
			self.init(uri.address,uri.objectID,uri.port,uri.protocol)
			return
		x=sre.match(r'(?P<protocol>[^\s:/]+)://(?P<hostname>[^\s:]+):?(?P<port>\d+)?/(?P<id>\S*)',arg)
		if x:
			self.protocol=x.group('protocol')
			self.address=x.group('hostname')
			self.port=x.group('port')
			if self.port:
				self.port=int(self.port)
			else:
				self.port=Pyro.config.PYRO_PORT
			self.objectID=x.group('id')
			return
		Log.error('PyroURI','illegal URI format passed: '+arg)
		raise URIError('illegal URI format')
	def getProxy(self):
		return DynamicProxy(self)
	def getAttrProxy(self):
		return DynamicProxyWithAttrs(self)


#
#	This method takes a string representation of a Pyro URI
#	and parses it. If it's a meta-protocol URI such as
#	PYRONAME://.... it will do what is needed to make
#	a regular PYRO:// URI out of it (resolve names etc).
#
def processStringURI(URI):
	# PYRONAME(SSL)://[hostname[:port]/]objectname
	x=sre.match(r'(?P<protocol>PYRONAME|PYRONAMESSL)://(((?P<hostname>[^\s:]+):(?P<port>\d+)/)|((?P<onlyhostname>[^\s:]+)/))?(?P<name>\S*)',URI)
	if x:
		import naming
		protocol=x.group('protocol')
		if protocol=="PYRONAMESSL":
			raise ProtocolError("NOT SUPPORTED YET: "+protocol) # XXX
		hostname=x.group('hostname') or x.group('onlyhostname')
		port=x.group('port')
		name=x.group('name')
		loc=naming.NameServerLocator()
		if port:
			port=int(port)
		NS=loc.getNS(host=hostname,port=port)
		return NS.resolve(name)
	# PYROLOC(SSL)://hostname[:port]/objectname
	x=sre.match(r'(?P<protocol>PYROLOC|PYROLOCSSL)://(?P<hostname>[^\s:]+):?(?P<port>\d+)?/(?P<name>\S*)',URI)
	if x:
		protocol=x.group('protocol')
		hostname=x.group('hostname')
		port=x.group('port')
		if port:
			port=int(port)
		else:
			port=0
		name=x.group('name')
		return PyroURI(hostname,name,port,protocol)
	if URI.startswith('PYROLOC') or URI.startswith('PYRONAME'):
		# hmm should have matched above. Likely invalid.
		raise URIError('invalid URI format')
	# It's not a meta-protocol such as PYROLOC or PYRONAME,
	# let the normal Pyro URI deal with it.
	# (it can deal with regular PYRO: and PYROSSL: protocols)
	return PyroURI(URI)


#############################################################################
#
#	DynamicProxy	- dynamic Pyro proxy
#
#	Can be used by clients to invoke objects for which they have no
#	precompiled proxy.
#
#############################################################################

def getProxyForURI(URI):
	return DynamicProxy(URI)
def getAttrProxyForURI(URI):
	return DynamicProxyWithAttrs(URI)

class DynamicProxy:
	def __init__(self, URI):
		_checkInit() # init required
		if type(URI) in (StringType,UnicodeType):
			URI=processStringURI(URI)
		self.URI = URI
		self.objectID = URI.objectID
		# Delay adapter binding to enable transporting of proxies.
		# We just create an adapter, and don't connect it...
		self.adapter = protocol.getProtocolAdapter(self.URI.protocol)
		self._name=[]
		# ---- don't forget to register local vars with DynamicProxyWithAttrs, see below
	def __del__(self):
		if 'adapter' in self.__dict__.keys():
			self.adapter.release(nolog=1)
	def _setIdentification(self, ident):
		self.adapter.setIdentification(ident)
	def _setNewConnectionValidator(self, validator):
		self.adapter.setNewConnectionValidator(validator)
	def _setOneway(self, methods):
		if type(methods) not in (type([]), type((0,))):
			methods=(methods,)
		self.adapter.setOneway(methods)
	def _setTimeout(self,timeout):
		self.adapter.setTimeout(timeout)
	def _release(self):
		if self.adapter:
			self.adapter.release()
	def __copy__(self):			# create copy of current proxy object
		c=DynamicProxy(self.URI)
		return c
	def __getattr__(self, name):
		if name!="__getinitargs__":			# allows it to be safely pickled
			self._name.append(name)
			return self.__invokePYRO__
		raise AttributeError()
	def __repr__(self):
		return "<"+self.__class__.__name__+" for "+str(self.URI)+">"
	def __str__(self):
		return repr(self)
	def __hash__(self):
		# makes it possible to use this class as a key in a dict
		return hash(self.objectID)
	def __lt__(self,other):
		# makes it possible to compare two proxies using objectID
		return self.objectID<other.objectID
	def __gt__(self,other):
		# makes it possible to compare two proxies using objectID
		return self.objectID>other.objectID
	def __eq__(self,other):
		# makes it possible to compare two proxies using objectID
		return self.objectID==other.objectID
	def __cmp__(self,other):
		# makes it possible to compare two proxies using objectID
		return cmp(self.objectID,other.objectID)
	def __nonzero__(self):
		return 1
	def __coerce__(self,other):  # XXX python 2.0.x calls this sometimes
		return (self,other)  # yep, this works! weird huh?

	def __invokePYRO__(self, *vargs, **kargs):
		if not self.adapter.connected():
			self.adapter.bindToURI(self.URI)
		return self.adapter.remoteInvocation(self._name.pop(),
						constants.RIF_VarargsAndKeywords, vargs, kargs)

	# Pickling support, otherwise pickle uses __getattr__:
	def __getstate__(self):
		# for pickling, return a non-connected copy of ourselves:
		copy = self.__copy__()
		copy._release()
		return copy.__dict__
		# this used to disconnect ourselves, but that is inefficient:
		# self._release()		# release socket to be able to pickle this object
		# return self.__dict__
	def __setstate__(self, args):
		# this appears to be necessary otherwise pickle won't work
		self.__dict__=args

	
class DynamicProxyWithAttrs(DynamicProxy):
	def __init__(self, URI):
		# first set the list of 'local' attrs for __setattr__
		self.__dict__["_local_attrs"] = ("_local_attrs","URI", "objectID", "adapter", "_name", "_attr_cache")
		self._attr_cache = {}
		DynamicProxy.__init__(self, URI)
	def _r_ga(self, attr, value=0):
		if value: self._name.append("_r_ga")
		else: self._name.append("_r_ha")
		return self.__invokePYRO__(attr)
	def findattr(self, attr):
		if attr in self._attr_cache.keys():
			return self._attr_cache[attr]
		# look it up and cache the value
		self._attr_cache[attr] = self._r_ga(attr)
		return self._attr_cache[attr]
	def __copy__(self):		# create copy of current proxy object
		c=DynamicProxyWithAttrs(self.URI)
		return c
	def __setattr__(self, attr, value):
		if attr in self.__dict__["_local_attrs"]:
			self.__dict__[attr]=value
		else:
			result = self.findattr(attr)
			if result==2: # attribute
				self._name.append("_r_sa")
				return self.__invokePYRO__(attr,value)
			else:
				raise AttributeError('not an attribute')
	def __getattr__(self, attr):
		# allows it to be safely pickled
		if attr not in ("__getinitargs__", "__hash__","__cmp__","__eq__"):
			result=self.findattr(attr)
			if result==1: # method
				self._name.append(attr)
				return self.__invokePYRO__
			elif result:
				return self._r_ga(attr, 1)
		raise AttributeError
		

#############################################################################
#
#	Daemon		- server-side Pyro daemon
#
#	Accepts and dispatches incoming Pyro method calls.
#
#############################################################################

# The pyro object that represents the daemon.
# The daemon is not directly remotely accessible, for security reasons.
class DaemonServant(ObjBase):
	def __init__(self, daemon):
		ObjBase.__init__(self)
		# XXX next stmt could be a cyclic reference if weakrefs are not implemented :-(
		self.daemon=util.weakref(daemon)
	def getRegistered(self):
		return self.daemon.getRegistered()
	def ResolvePYROLOC(self, name):
		return self.daemon.ResolvePYROLOC(name)
		
# The daemon itself:
class Daemon(protocol.TCPServer, ObjBase):
	def __init__(self,prtcol='PYRO',host='',port=0,norange=0,publishhost=None):
		ObjBase.__init__(self)
		self.NameServer = None
		self.connections=[]
		_checkInit("server") # init required
		self.setGUID(constants.INTERNAL_DAEMON_GUID)
		self.implementations={constants.INTERNAL_DAEMON_GUID:(DaemonServant(self),'__PYRO_Internal_Daemon')}
		self.persistentConnectedObjs=[] # guids
		self.transientsCleanupAge=0
		self.transientsMutex=util.getLockObject()
		if port:
			self.port = port
		else:
			self.port = Pyro.config.PYRO_PORT
		if norange:
			portrange=1
		else:
			portrange=Pyro.config.PYRO_PORT_RANGE
		if not publishhost:
			publishhost=host
		errormsg=''
		for i in range(portrange):
			try:
				protocol.TCPServer.__init__(self, self.port, host, Pyro.config.PYRO_MULTITHREADED,prtcol)
				self.hostname = publishhost or protocol.getHostname()
				self.protocol = prtcol
				self.adapter = protocol.getProtocolAdapter(prtcol)
				self.validateHostnameAndIP()  # ignore any result message... it's in the log already.
				return
			except ProtocolError,msg:
				errormsg=msg
				self.port+=1
		Log.error('Daemon','Couldn\'t start Pyro daemon: ' +str(errormsg))
		raise DaemonError('Couldn\'t start Pyro daemon: ' +str(errormsg))
	
	def __del__(self):
		# server shutting down, unregister all known objects in the NS
		if self.NameServer and constants:
			del self.implementations[constants.INTERNAL_DAEMON_GUID]
			if self.implementations:
				Log.warn('Daemon','Shutting down but there are still',len(self.implementations),'objects connected - disconnecting them')
			for guid in self.implementations.keys():
				if guid not in self.persistentConnectedObjs:
					(obj,name)=self.implementations[guid]
					if name:
						try:
							self.NameServer.unregister(name)
						except Exception,x:
							Log.warn('Daemon','Error while unregistering object during shutdown:',x)
		if hasattr(self,'adapter'):
			del self.adapter
		if protocol: protocol.TCPServer.__del__(self)

	def __str__(self):
		return '<Pyro Daemon on '+self.hostname+':'+str(self.port)+'>'
	def __getstate__(self):
		from pickle import PicklingError
		raise PicklingError('no access to the daemon')

	def validateHostnameAndIP(self):
		# Checks if hostname is sensible. Returns None if it is, otherwise a message
		# telling what's wrong if it isn't too serious. If things are really bad,
		# expect an exception to be raised. Things are logged too.
		import socket
		if not self.hostname:
			Log.error("Daemon","no hostname known")
			raise socket.error("no hostname known for daemon")
		if self.hostname!="localhost":
			ip = protocol.getIPAddress(self.hostname)
			if ip is None:
				Log.error("Daemon","no IP address known")
				raise socket.error("no IP address known for daemon")
			if ip!="127.0.0.1":
				return None  # this is good!
		# 127.0.0.1 or 'localhost' is a warning situation!
		msg="daemon bound on hostname that resolves to loopback address 127.0.0.1"
		Log.warn("Daemon",msg)
		Log.warn("Daemon","hostname="+self.hostname)
		print "\nWARNING: "+msg+"\n"
		return msg
	
	def useNameServer(self,NS):
		self.NameServer=NS
	def getNameServer(self):
		return self.NameServer
	def setTimeout(self, timeout):
		self.adapter.setTimeout(timeout)
	def setAllowedIdentifications(self, ids):
		self.getNewConnectionValidator().setAllowedIdentifications(ids)
	def setTransientsCleanupAge(self, secs):
		self.transientsCleanupAge=secs
		if self.threaded:
			Log.msg('Daemon','creating Grim Reaper thread for transients, timeout=',secs)
			from threading import Thread
			reaper=Thread(target=self._grimReaper)
			reaper.setDaemon(1)   # thread must exit at program termination.
			reaper.start()
	def _grimReaper(self):
		# this runs in a thread.
		while self.transientsCleanupAge>0:
			time.sleep(self.transientsCleanupAge/5)
			self.reapUnusedTransients()

	def getProxyForObj(self, obj):
		return DynamicProxy( PyroURI(self.hostname,
				obj.GUID(), prtcol=self.protocol, port=self.port) )
	def getAttrProxyForObj(self, obj):
		return DynamicProxyWithAttrs( PyroURI(self.hostname,
				obj.GUID(), prtcol=self.protocol, port=self.port) )

	def connectPersistent(self, object, name=None):
		# when a persistent entry is found in the NS, that URI is
		# used instead of the supplied one, if the address matches.
		if name and self.NameServer:
			try:
				newURI = PyroURI(self.hostname, object.GUID(), prtcol=self.protocol, port=self.port)
				URI=self.NameServer.resolve(name)
				if (URI.protocol,URI.address,URI.port)==(newURI.protocol,newURI.address,newURI.port):
					# reuse the previous object ID
					object.setGUID(URI.objectID)
					# enter the (object,name) in the known impl. dictionary
					self.implementations[object.GUID()]=(object,name)
					self.persistentConnectedObjs.append(object.GUID())
					object.setDaemon(self)
					return URI
				else:
					# name exists, but address etc. is wrong. Remove it.
					# then continue so it wil be re-registered.
					try: self.NameServer.unregister(name)
					except NamingError: pass
			except NamingError:
				pass
		# Register normally.		
		self.persistentConnectedObjs.append(object.GUID())
		return self.connect(object, name)

	def connect(self, object, name=None):
		URI = PyroURI(self.hostname, object.GUID(), prtcol=self.protocol, port=self.port)
		# if not transient, register the object with the NS
		if name:
			if self.NameServer:
				self.NameServer.register(name, URI)
			else:
				Log.warn('Daemon','connecting object without name server specified:',name)
		# enter the (object,name) in the known implementations dictionary
		self.implementations[object.GUID()]=(object,name)
		object.setDaemon(self)
		return URI

	def disconnect(self,object):
		try:
			if self.NameServer and self.implementations[object.GUID()][1]:
				# only unregister with NS if it had a name (was not transient)
				self.NameServer.unregister(self.implementations[object.GUID()][1])
			del self.implementations[object.GUID()]
			if object.GUID() in self.persistentConnectedObjs:
				self.persistentConnectedObjs.remove(object.GUID())
			# XXX Clean up connections/threads to this object?
			#     Can't be done because thread/socket is not associated with single object 
		finally:
			object.setDaemon(None)

	def getRegistered(self):
		r={}
		for guid in self.implementations.keys():
			r[guid]=self.implementations[guid][1]	# keep only the names
		return r

	def handleInvocation(self, conn):	# overridden from TCPServer
		# called in both single- and multithreaded mode
		self.getLocalStorage().caller=conn
		self.getAdapter().handleInvocation(self, conn)
		self.reapUnusedTransients()

	def reapUnusedTransients(self):
		if not self.transientsCleanupAge: return
		now=time.time()
		self.transientsMutex.acquire()
		try:
			for (obj,name) in self.implementations.values()[:]:   # use copy of list
				if not name:
					# object is transient, reap it if timeout requires so.
					if (now-obj.lastUsed)>self.transientsCleanupAge:
						self.disconnect(obj)
						obj._gotReaped()
		finally:
			self.transientsMutex.release()

	def handleError(self,conn):			# overridden from TCPServer
		try:
			(exc_type, exc_value, exc_trb) = sys.exc_info()
			if exc_type==ProtocolError:
				# Problem with the communication protocol, shut down the connection
				# XXX is this wat we want???
				Log.error('Daemon','protocol error occured:',exc_value)
				Log.error('Daemon','Due to network error: shutting down connection with',conn)
				self.removeConnection(conn)
			else:
				exclist = Pyro.util.formatTraceback(exc_type, exc_value, exc_trb)
				out =''.join(exclist)
				Log.warn('Daemon', 'Exception during processing of request from',
					conn,' type',exc_type,
					'\n--- traceback of this exception follows:\n',
					out,'\n--- end of traceback')
				if exc_type==PyroExceptionCapsule:
					sys.stdout.flush()
					# This is a capsuled exception, used with callback objects.
					# That means we are actually the daemon on the client.
					# Return the error to server and raise exception locally once more.
					# (with a normal exception, it is not raised locally again!)
					self.adapter.returnException(conn,exc_value.excObj,0,exclist) # don't shutdown
					exc_value.raiseEx()
				else:
					# normal exception
					self.adapter.returnException(conn,exc_value,0,exclist) # don't shutdown connection

		finally:
			# clean up circular references to traceback info
			del exc_type, exc_value, exc_trb

	def getAdapter(self):
		# overridden from TCPServer
		return self.adapter

	def ResolvePYROLOC(self, name):
		# this gets called from the protocol adapter when
		# it wants the daemon to resolve a local object name (PYROLOC: protocol)
		Log.msg('Daemon','resolving PYROLOC name: ',name)
		for o in self.implementations.keys():
			if self.implementations[o][1]==name:
				return o
		raise NamingError('no object found by this name')


#############################################################################
#
#	Client/Server Init code
#
#############################################################################

# Has init been performed already?
_init_server_done=0
_init_client_done=0
_init_generic_done=0

def _initGeneric_pre():
	global _init_generic_done
	if _init_generic_done:
		return
	if Pyro.config.PYRO_TRACELEVEL == 0: return
	try:
		out='\n'+'-'*60+' NEW SESSION\n'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+ \
			'   Pyro Initializing, version '+constants.VERSION+'\n'
		Log.raw(out)
	except IOError,e:
		sys.stderr.write('PYRO: Can\'t write the tracefile '+Pyro.config.PYRO_LOGFILE+'\n'+str(e))

def _initGeneric_post():
	global _init_generic_done
	setattr(Pyro.config, Pyro.constants.CFGITEM_PYRO_INITIALIZED,1)
	if Pyro.config.PYRO_TRACELEVEL == 0: return
	try:
		if not _init_generic_done:
			out='Configuration settings are as follows:\n'
			for item in dir(Pyro.config):
				if item[0:4] =='PYRO':
					out+=item+' = '+str(Pyro.config.__dict__[item])+'\n'
			Log.raw(out)
		Log.raw('Init done.\n'+'-'*70+'\n')
	except IOError:
		pass
	_init_generic_done=1	


def initClient(banner=1):
	global _init_client_done
	if _init_client_done: return
	_initGeneric_pre()
	if Pyro.config.PYRO_TRACELEVEL >0: Log.raw('This is initClient.\n')
	Pyro.config.finalizeConfig_Client()
	_initGeneric_post()
	if banner:
		print 'Pyro Client Initialized. Using Pyro V'+constants.VERSION
	_init_client_done=1
	
def initServer(banner=1, storageCheck=1):
	global _init_server_done
	if _init_server_done: return
	_initGeneric_pre()
	if Pyro.config.PYRO_TRACELEVEL >0: Log.raw('This is initServer.\n')
	Pyro.config.finalizeConfig_Server(storageCheck=storageCheck)
	_initGeneric_post()
	if banner:
		print 'Pyro Server Initialized. Using Pyro V'+constants.VERSION
	_init_server_done=1

