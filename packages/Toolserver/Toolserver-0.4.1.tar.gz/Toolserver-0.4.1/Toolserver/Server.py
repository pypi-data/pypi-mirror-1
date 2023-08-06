"""

Tool Server Framework - main server module

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

import os
import re
import sys
import time
import glob
import signal
import asyncore
import threading

from Toolserver.Config import config
from Toolserver.Context import context
from Toolserver.Daemonize import become_daemon
from Toolserver.Utils import StringIO, logInfo, logWarning, logError, EmptyResult
from Toolserver.Tool import getTools
from Toolserver.RPCHandler import getRegisteredRPCHandlers
from Toolserver.RESTHandler import rest_handler
from Toolserver.HTTPHandler import http_handler
from Toolserver.RewriteHandler import rewrite_handler
from Toolserver.timeoutsocket import setDefaultSocketTimeout
from Toolserver.Worker import dispatcher, start_worker
from Toolserver import autoreload

# import default RPC handlers statically (they can be loaded from any tools
# directory, too)
import SOAPHandler
import XMLRPCHandler

from medusa import http_server, status_handler, logger, filesys, monitor, default_handler

# Add features to medusa to allow producers to tell the server that they
# don't have anything to return currently. This is different from the empty
# string, as the empty string is the EOF mark in medusa. So we introduce
# an exception to tell about this fact.

class Channel(http_server.http_channel):
	"""
	This channell just introduces a special handling for EmptyResult
	exceptions. These are thrown by producers that want to tell about
	no current results but don't want to be closed.
	"""

	def refill_buffer(self):
		try:
			http_server.http_channel.refill_buffer(self)
		except EmptyResult:
			return

class Server(http_server.http_server):

	channel_class = Channel

setDefaultSocketTimeout(config.timeout)

def terminate(signal="(API shutdown)", param=None):
	"""Signal handler for the daemon.  Applicable
	only to those systems implementing POSIX signals.
	"""
	termination(signal)

def termination(signal, exitcode=0):
	"""
	inner code to terminate the server. This does the hard work.
	"""
	ctime = time.asctime( time.localtime( time.time() ) )
	logWarning("Received signal %s terminating at %s", signal, ctime)
	for tool in getTools():
		if hasattr(tool, '_shutdown'):
			logInfo('shutting down tool %s' % tool.name)
			try:
				tool._begin()
				tool._shutdown()
			except:
				tool._abort()
				raise
			else:
				tool._commit()
	dispatcher.stop()
	for tool in getTools():
		if hasattr(tool, '_terminate'):
			logInfo('terminating tool %s' % tool.name)
			tool._terminate()
	if os.path.exists(config.PIDFILE): os.remove(config.PIDFILE)
	sys.exit(exitcode)

def install_handlers():
	import signal
	logInfo("Installing signal handlers")
	#install default signal profile
	signalHandlers = (
		('SIGTTOU', signal.SIG_IGN),
		('SIGTTIN', signal.SIG_IGN),
		('SIGCHLD', signal.SIG_IGN),
		('SIGTSTP', terminate),
		('SIGTERM', terminate),
		('SIGINT', terminate),
	)
	# register the handler that are supported on this platform
	for (sigID, function) in signalHandlers:
		sigNumber = getattr(signal, sigID, None)
		if sigNumber != None:
			signal.signal(sigNumber, function)

def load_dynamic_tools():
	# import dynamically installed tools in the tools directory
	thash = {}
	for el in glob.glob("%s/*.py" % config.MASTERTOOLDIR):
		fn = os.path.splitext(os.path.basename(el))[0]
		if not thash.has_key(fn):
			thash[fn] = el
	for el in glob.glob("%s/*.py" % config.TOOLDIR):
		fn = os.path.splitext(os.path.basename(el))[0]
		if not thash.has_key(fn):
			thash[fn] = el
	tlist = map(lambda k: (k, thash[k]), thash.keys())
	sys.path.insert(0, config.LIBDIR)
	sys.path.insert(0, config.MASTERTOOLDIR)
	sys.path.insert(0, config.TOOLDIR)
	for (tool, toolfile) in tlist:
		logInfo("Installing tool %s", tool)
		eval(compile("import %s" % tool, toolfile, 'exec'))

def configure_tools():
	for tool in getTools():
		logInfo('Initializing tool options %s, stage 0 - configuration', tool.name)
		tool._defaults()
		tool._configure()

def initialize_tools():
	for tool in getTools():
		logInfo('Initializing tool options %s, stage 1 - queues, db', tool.name)
		tool._initqueues(**tool._options)
		tool._initdb(**tool._options)
	for tool in getTools():
		logInfo('Initializing tool options %s, stage 2 - options', tool.name)
		try:
			context._begin()
			try:
				tool._begin()
				tool._initopts(**tool._options)
			except:
				tool._abort()
				raise
			else:
				tool._commit()
		finally: context._end()

def start_server(daemon=1):
	install_handlers()
	if daemon:

		for file in ('etc.log', 'error.log'):
			fname = os.path.join(config.LOGDIR, file)
			if os.path.exists(fname):
				os.unlink(fname)

		logInfo('Changing log redirection')
		become_daemon(
			config.VARDIR,
			os.path.join(config.LOGDIR, 'etc.log'),
			os.path.join(config.LOGDIR, 'error.log')
		)
	else:
		# if not daemon, still change current directory (otherwise
		# that's a side effect of become_daemon)
		os.chdir(config.VARDIR)

	def inner_run():
		load_dynamic_tools()
		configure_tools()
		initialize_tools()

		hs = None
		accessLog = None
		log = None

		ms = None

		accessLog = logger.rotating_file_logger(
			os.path.join(config.LOGDIR, 'access.log'), None, 1024*1024
		)
		log = status_handler.logger_for_status(accessLog)

		hs = Server(
			config.serverip,
			config.serverport,
			None,
			log
		)
		hs.server_name = config.serverhostname

		if config.monitorport and config.monitorpassword:
			ms = monitor.secure_monitor_server(
				config.monitorpassword,
				config.serverip,
				config.monitorport
			)

		rootfs = filesys.os_filesystem(config.ROOTDIR)
		if config.basicauth:
			httph = http_handler(rootfs)
		else:
			httph = default_handler.default_handler(rootfs)
		hs.install_handler(httph)

		for klass in getRegisteredRPCHandlers():
			hs.install_handler(klass())

		resth = rest_handler()
		hs.install_handler(resth)

		statush = status_handler.status_extension((hs,))
		hs.install_handler(statush)

		# the rewrite handler must be installed last so that it
		# is processed first!
		rwh = rewrite_handler()
		hs.install_handler(rwh)

		start_worker()

		logWarning("Server is now up and responding")
		asyncore.loop()

	mypid = os.getpid()
	pidf = open(config.PIDFILE, "w")
	pidf.write('%d\n%d' % (mypid, config.serverport))
	pidf.close()

	if config.autoreload:
		autoreload.install_terminator(termination)
		autoreload.main(inner_run)
	else: inner_run()

def stop_server():
	mypid = 0
	try:
		pidf = open(config.PIDFILE)
		mypid = int(pidf.readline())
		pidf.close()
	except:
		logError("Error while reading PID for desktop server")
	if mypid:
		try:
			logWarning("Sending signal TERM to pid %d", mypid)
			os.kill(mypid, signal.SIGTERM)
		except:
			logError("Error while trying to kill desktop server")

