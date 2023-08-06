"""

Toolserver Framework for Python - Tool base class

Copyright (c) 2002, Georg Bauer <gb@rfc1437.de>

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 
the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys
import os
import re
import time
import types
import traceback
import weakref
import threading

from medusa import http_server
from medusa import filesys

import Toolserver

from Toolserver.DefaultConfig import Configuration
from Toolserver.Config import config
from Toolserver.Context import context
from Toolserver.Worker import dispatcher
from Toolserver.AsyncCall import async_call, createAsyncId, checkAsyncIdRunning
from Toolserver.Utils import logWarning, logError, logInfo, AuthError, ForbiddenError, ObsoleteError
from Toolserver.ProcessQueue import PriorityEvent, TimerEvent, ProcessingQueue
from Toolserver.Linda import universe

version = 'Toolserver Framework for Python %s (http://pyds.muensterland.org/)' % Toolserver.__version__
shortversion = 'TooFPy/%s' % Toolserver.__version__

# Registration of installed tools and their namespaces. Tools
# are registered as a tuple (class, title, desc, level)
# and are instantiated once per thread (the cache has the
# thread as key)
_ToolNamespace = {}

# register a tool into the registry
def registerTool(klass, name, *args, **kw):
	if type(name) == types.StringType:
		name = name.split('.')
	if type(name) == types.ListType:
		name = tuple(name)
	assert type(name) == types.TupleType, "Name must be either string or tuple"
	if not _ToolNamespace.has_key(len(name)):
		_ToolNamespace[len(name)] = {}
	_ToolNamespace[len(name)][name] = klass(name, *args, **kw)

# this checks wether a tool exists.
def hasTool(name):
	if type(name) == types.StringType:
		name = name.split('.')
	if type(name) == types.ListType:
		name = tuple(name)
	assert type(name) == types.TupleType, "Name must be either string or tuple"
	if _ToolNamespace.has_key(len(name)):
		if _ToolNamespace[len(name)].has_key(name):
			return 1
	if len(name):
		tid = name[-1]
		name = name[:-1]
		try:
			tool = getTool(name)
			if tool._factory:
				return tool.has_key(tid)
		except KeyError:
			return 0
	return 0

# get a list of installed tools (only registered tools, not transient tools!)
def getTools():
	liste = []
	for l in _ToolNamespace.keys():
		for k in _ToolNamespace[l].keys():
			liste.append(weakref.proxy(_ToolNamespace[l][k]))
	liste.sort(lambda a, b: -1*cmp(len(a.name), len(b.name)))
	return liste

# get a tool by name
def getTool(name):
	if type(name) == types.StringType:
		name = name.split('.')
	if type(name) == types.ListType:
		name = tuple(name)
	assert type(name) == types.TupleType, "Name must be either string or tuple"
	if _ToolNamespace.has_key(len(name)):
		if _ToolNamespace[len(name)].has_key(name):
			return weakref.proxy(_ToolNamespace[len(name)][name])
	if len(name):
		tid = name[-1]
		name = name[:-1]
		tool = getTool(name)
		if tool._factory:
			return tool[tid]
	raise KeyError(name)

# this checks wether an existing tool has a specified method
def hasToolMethod(name, methname):
	try:
		return hasattr(getTool(name), methname)
	except:
		return 0

# this gets a tool and it's method for a given path
def getToolForPath(path):
	assert path[0] == '/', "only absolute paths can be used"
	parts = path[1:].split('/')
	try:
		return (getTool(parts), 'index')
	except KeyError:
		if len(parts):
			method = parts.pop()
			return (getTool(parts), method or 'index')
	raise KeyError(parts)

# this gets the first tool that's in the path of a URL. This can
# be used to build hierarchical tool responsibilities (like authentication
# for static content in the namespace of tools). It additionally returns a
# list of parts for the path after the tools main address.
def getFirstToolForPath(path):
	assert path[0] == '/', "only absolute paths can be used"
	parts = path[1:].split('/')
	try:
		# this is a direct tool for a URL
		return (getTool(parts), [])
	except KeyError:
		rest = []
		while len(parts):
			# go up in the parts list to find the first
			# matching tool
			rest = [parts.pop()]+rest
			try: return (getTool(parts), rest)
			except KeyError: pass
	raise KeyError(parts)

class StandardTool:

	"""
	This tool implements the basic functionality of all
	tools available.

	This is the abstract class - either you instantiated an
	abstract class, or the programmer forgot to give a meaningfull
	description.
	"""

	_deflate = 1
	_content_type = 'text/xml'
	_types = (
		('functionNameList', ['string']),
	)

	def __init__(self, name, **kw):
		self.name = name
		self.uri = '/' + '/'.join(name)
		self.asyncResults = {}
		self.asyncExceptions = {}
		self._options = kw
		self._lock = threading.RLock()
		self._locker = '?'
		self._factory = 0
		self._realm = '.'.join(name)+'@'+config.serverhostname
		self._checkrsa = 0
		self.config = Configuration()
	
	# This method is called before the _configure method is
	# called on all classes. This allows to set up default values
	# for configuration parameters. Just overload this method
	# and set attributes of the self.config instance variable.
	# You MUST give defaults for all parameters you want to be
	# able to set in the module configuration!
	def _defaults(self):
		pass
	
	# This is a method that checks for a configuration module
	# for this specific tool in the ~/.Toolserver/etc/ path
	# and fills instance variables with key-value pairs from
	# that module. This can be used to move configuration out
	# of the module source. Only config options that are defined
	# in _default are set. The configuration file is named
	# by the namespace elements, capitalized and concatenated,
	# additional a Config suffix is appended. So a tool with
	# the namespace (anton, berta, caesar) is configured by
	# ~/.Toolserver/etc/AntonBertaCaesarConfig.py
	def _configure(self):
		cfg = ''.join(map(lambda el: el.capitalize(), self.name))+'Config'
		try:
			eval(compile("import %s" % cfg, cfg+'.py', 'exec'))
			hasconfig = 1
		except ImportError:
			hasconfig = 0
		if hasconfig:
			module = sys.modules[cfg]
			for k in module.__dict__.keys():
				if self.config.has_key(k) and not k.startswith('_'):
					self.config[k] = module.__dict__[k]

	# This is a method that writes out the configuration for this tool
	# to the default file name
	def _writeConfig(self):
		cfg = ''.join(map(lambda el: el.capitalize(), self.name))+'Config'
		cfgpath = os.path.join(config.ETCDIR, '%s.py' % cfg)
		self.config.write(cfgpath)
		if not os.stat(cfgpath)[6]:
			os.unlink(cfgpath)
			try: os.unlink(cfgpath+'c')
			except OSError, e: pass
	
	# This is an init hook that sets up queues. This is factored
	# out so that sub tools might have different initialization
	# needs - for example transient tools reuse the queues
	# from the factory. All additional parameters to __init__
	# are passed along.
	def _initqueues(self, **kw):
		self._timer = ProcessingQueue(self, 'timer', TimerEvent, sync=0)
		self._queue = ProcessingQueue(self, 'queue', PriorityEvent, sync=1)
	
	# This is an init hook that can be overloaded to do stuff that
	# must be done outside of transactional control at server startup.
	# Usually you use it to build database connections. All additional
	# parameters form __init__ are passed along.
	def _initdb(self, **kw):
		pass

	# This is an init hook that can be overloaded. All _initopts
	# are called after all tools are instantiated! This can have
	# additional parameters - it get's all additional parameters
	# from the __init__ call. This method is called under transactional
	# control, so if you want to set up databases, you should hook
	# up this here! This is called in stage 2 and all other tools are
	# at least up to _initdb, so you should be able to call other tools
	# already.
	def _initopts(self, **kw):
		pass

	# this returns the name as a path element
	def _getNameAsPath(self):
		if self.name == ():
			return '/'
		else:
			return '/' + '/'.join(self.name) + '/'
	
	# this returns a path to a method
	def _getMethodAsPath(self, method, **kw):
		if hasattr(self, method):
			methpath = self._getNameAsPath() + method
			if kw:
				parms = map(lambda k: '%s=%s' % (k, kw[k]), kw.keys())
				parms = '&'.join(parms)
				methpath += '?'
				methpath += parms
			return methpath
		else:
			raise AttributeError(method)

	# this method pushes a function call into the background so
	# they are executed by the workers. Results are kept for later
	# query.
	def _async(self, fun, *args, **kw):
		asyncid = createAsyncId(self)
		dispatcher.append(self, async_call, (args, kw, asyncid, 1), fun)
		return asyncid

	# this method pushes a function call into the background so
	# they are executed by the workers. It doesn't keep results around,
	# as does _async!
	def _asyncProc(self, proc, *args, **kw):
		asyncid = createAsyncId(self)
		dispatcher.append(self, async_call, (args, kw, asyncid, 0), proc)
		return asyncid

	# this method checks wether an async call is still active
	def _asyncActive(self, asyncid):
		if checkAsyncIdRunning(asyncid): return 1
		else: return 0

	# this method returns the result of a async call. It's not there
	# if the call crashed! After access the result is deleted from
	# the result cache!
	def _asyncResult(self, asyncid):
		try: 
			if self.asyncResults.has_key(asyncid):
				return self.asyncResults[asyncid]
			elif self.asyncExceptions.has_key(asyncid):
				raise self.asyncExceptions[asyncid]
			raise KeyError(asyncid)
		finally:
			try: del self.asyncResults[asyncid]
			except KeyError: pass
			try: del self.asyncExceptions[asyncid]
			except KeyError: pass

	# this method times an event for later execution. The timespec
	# is the time in epoch. The result can be fetched with _asyncResult,
	# if the event is neither _timedWaiting nor _asyncActive
	def _timed(self, timespec, method, *args, **kw):
		return self._timer.queueCall(timespec, method, 1, args, kw)

	# this method times an event for later execution. The timespec
	# is the time in epoch. The result is not kept.
	def _timedProc(self, timespec, method, *args, **kw):
		return self._timer.queueCall(timespec, method, 0, args, kw)
	
	# this method checks wether a timer event is still waiting
	def _timedWaiting(self, asyncid):
		return self._timer.queueWaiting(asyncid)

	# this method queues an event for later execution. The timespec
	# is the time in epoch. The result can be fetched with _asyncResult,
	# if the event is neither _timedWaiting nor _asyncActive
	def _queued(self, priority, method, *args, **kw):
		return self._queue.queueCall((priortiy, time.time()), method, 1, args, kw)

	# this method queues an event for later execution. The timespec
	# is the time in epoch. The result is not kept.
	def _queuedProc(self, priority, method, *args, **kw):
		return self._queue.queueCall((priortiy, time.time()), method, 0, args, kw)
	
	# this method checks wether a timer event is still waiting
	def _queuedWaiting(self, asyncid):
		return self._queue.queueWaiting(asyncid)

	# this method checks wether a timed event is 
	# this method checks wether a timed event is 
	# These methods lock areas of your tool against multithreaded
	# access to protect your tool against data corruption. Use this
	# only if really needed, as too much locks will degraed
	# your tools performance!
	def _acquire(self, blocking=1):
		if config.verbose:
			f = traceback.extract_stack()
			try: method = f[-2][2]
			except IndexError, KeyError: method = '??'
			if blocking:
				if not self._lock.acquire(blocking=0):
					now = time.time()
					print "<%s.%s>: waiting for lock by <%s> at %s" % (
						'.'.join(self.name),
						method,
						self._locker,
						time.ctime(now)
					)
					self._lock.acquire(blocking=1)
					then = time.time()
					print "<%s.%s>: acquired lock from <%s> at %s after %d seconds" % (
						'.'.join(self.name),
						method,
						self._locker,
						time.ctime(then),
						int(then-now)
					)
			else: self._lock.acquire(blocking=0)
			self._locker = '.'.join(self.name) + '.' + method
		else: self._lock.acquire()
	
	def _release(self):
		self._lock.release()

	# These methods are transaction control hooks. They are called
	# around any method invocation and can be overloaded by subclasses
	# to transparently hook up database transactions. Transaction
	# hooks are only automatich with RPC calls - if you call methos
	# internally, you have to do your own transaction handling!
	def _begin(self):
		pass
	
	def _abort(self):
		pass
	
	def _commit(self):
		pass
	
	# this method returns the file storage pathname. The path
	# is automatically created if it doesn't already exist.
	# you can pass in additional filesystem parts. You can
	# pass in a private flag that tells the system to not
	# use the ROOTDIR, but the VARDIR instead.
	def _filestorage(self, *parts, **kw):
		path = config.ROOTDIR
		if kw.has_key('private') and kw['private']:
			path = config.VARDIR
		for name in self.name:
			path = os.path.join(path, name)
		for part in parts:
			path = os.path.join(path, part)
		if not os.path.isdir(path): os.makedirs(path)
		return path

	# this method stores a file in the www directory under the
	# namespace of the module. Content is only stored if it really
	# differs from an already existing file. The filename can be
	# relative to the _filestorage path in URL notation (it can include
	# directories that are seperated by /). The same private flag can
	# be passed in as with _filestorage.
	def _store(self, filename, content, private=0):
		dirparts = os.path.dirname(filename).split('/')
		filename = os.path.basename(filename)
		if private: path = apply(self._filestorage, dirparts, {'private':private})
		else: path = self._filestorage(*dirparts)
		filename = os.path.join(path, filename)
		if os.path.exists(filename):
			oldcontent = open(filename).read()
			if oldcontent != content:
				open(filename, 'wb').write(content)
		else:
			open(filename, 'wb').write(content)
	
	# this method opens a file in the filestorage
	def _open(self, filename, mode='rb', private=0):
		dirparts = os.path.dirname(filename).split('/')
		filename = os.path.basename(filename)
		if private: path = apply(self._filestorage, dirparts, {'private':private})
		else: path = self._filestorage(*dirparts)
		filename = os.path.join(path, filename)
		return open(filename, mode)
	
	# this method loads a file from the filestorage
	def _load(self, filename, private=0):
		return self._open(filename, mode='rb', private=private).read()
	
	# this method checks wether a file is available in the filestorage
	def _exists(self, filename, private=0):
		dirparts = os.path.dirname(filename).split('/')
		filename = os.path.basename(filename)
		if private: path = apply(self._filestorage, dirparts, {'private':private})
		else: path = self._filestorage(*dirparts)
		filename = os.path.join(path, filename)
		if os.path.exists(filename): return 1
		else: return 0
	
	# this method puts a notification tuple into the Linda universe, so
	# that interested parties can hook to this notification and react
	# on changes that your tool is willing to publish. Notifications
	# only live for 5 Minutes in the TupleSpace. The tag should be
	# a string descriptor, the arguments can be any objects.
	def _notify(self, tag, *args):
		tuple = (tag, self.name) + args
		universe.outLimited(300, tuple)
	
	# this is a shorthand for waiting on a notification record in the
	# Linda universe. The args are the same spec as for the
	# Toolserver.Linda.Matcher class. Be informed that the tag
	# and a tuple (for the tool name) are prepended to the pattern,
	# though. This just waits for 5 minutes. If no event occured within
	# this time (or if the server is shut down before that time), a
	# KeyError will be thrown! If the tool is None, it waits for
	# any tool.
	def _wait(self, tool, tag, *args):
		if tool is None:
			pattern (tag, types.TupleType) + args
		else:
			if not isinstance(tool, StandardTool):
				tool = getTool(tool)
			pattern (tag, tool.name) + args
		return universe.keepWait(300, self.name, pattern)
	
	# this method returns a list with method names without _ in them
	def listRegisteredFunctions(self):
		"""
		This method lists all registered functions for this
		tool. It is used for introspection.
		"""
		liste = []
		for el in dir(self):
			if el.find('_') < 0:
				if hasattr(getattr(self, el), '__call__'):
					liste.append(el)
		return liste
	
	listRegisteredFunctions_signature = ('typens:functionNameList',)

	def listRegisteredFunctions_validate_RPC(self):
		return ''


class InternalTool(StandardTool):

	"""
	This is an abstract base class for internal tools that should
	not be called from the outside. This class just defines default
	validation wrappers. You can override validation for single
	methods in subclasses, of course, so this is actually just
	a differently tuned base class for tools with mostly internal
	methods. We use this to still enable access to the introspection
	method listRegisteredFunctions. So the real difference is that
	with this base class you have to explicitely allow access to
	methods, while with StandardTool allowed access is the default.
	The LOCAL RPC protocol is allowed, so that you can use both direct
	access or SyncCall access to methods (SyncCall allows you to use
	programming by contract even for local internal calls).

	This is the abstract class - either you instantiated an
	abstract class, or the programmer forgot to give a meaningfull
	description.
	"""

	def _validate(self, request, user, password):
		raise ForbiddenError('internal')

	def _validate_RPC_LOCAL(self, *args, **kw):
		return ''

	def _validate_RPC(self, *args, **kw):
		raise ForbiddenError('internal')

	
class ObsoleteTool(StandardTool):
	"""
	This tool is obsolete. As a result every call to every method
	in this tool will just raise an ObsoleteError. It's just installed
	as a placeholder that tells users and programmers what happened to
	some tool that was connected to this namespace.
	"""

	# define method names to send out
	_methods = ()

	def _raiser(self, name):
		__name = name
		__tool = self.name

		def obsoleteMethod(*args, **kw):
			logInfo('obsolete method %s in tool %s', __name, '.'.join(__tool))
			raise ObsoleteError(__tool + (__name,))
		return obsoleteMethod

	def __getattr__(self, name):
		if name in self._methods:
			return self._raiser(name)
		else: raise AttributeError(name)

