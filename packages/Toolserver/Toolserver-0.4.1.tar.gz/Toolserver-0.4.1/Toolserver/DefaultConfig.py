"""

Toolserver Framework for Python - Default Configuration

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
import sys
import copy
from distutils.sysconfig import PREFIX

try:
	import Crypto
	hasCrypto = 1
except ImportError: hasCrypto = 0

# this method constructs pathnames and creates those directories
# if they don't already exist
def constructPath(*args, **kw):
	path = apply(os.path.join, args)
	try: os.makedirs(path)
	except: pass
	if kw.get('mode',0): os.chmod(path, kw['mode'])
	return path

# This class encapsulates a simple configuration object.
# The main functionality is that this class mimiks a dictionary.
class Configuration:

	def __getitem__(self, key):
		return getattr(self, key)

	def __setitem__(self, key, value):
		setattr(self, key, value)

	def has_key(self, key):
		return hasattr(self, key)

	def keys(self):
		liste = filter(lambda a: a[0] >= 'a' and a[0] <= 'z', self.__dict__.keys())
		liste.sort()
		return liste

	def write(self, filename):
		cfg = open(filename, 'w')
		for k in self.keys():
			cfg.write('%s=%s\n' % (k, repr(self[k])))
		cfg.close()

# This class encapsulates the whole configuration business. There
# is usually only one instance of it, but data returned might be
# different on a per thread view
class SystemConfiguration(Configuration):

	def __init__(self, prefix, homedir):
		self.setPathVars(prefix, homedir)
		self.setPidFileVar()
		self._sections = []
	
	def setPathVars(self, prefix, homedir):
		self.PREFIX = prefix
		self.HOMEDIR = homedir
		self.SHAREDDIR = constructPath(self.PREFIX, 'share', 'toolserver')
		self.MASTERTOOLDIR = constructPath(self.SHAREDDIR, 'tools')
		self.ROOTDIR = constructPath(self.HOMEDIR, 'www', mode=0700)
		self.LOGDIR = constructPath(self.HOMEDIR, 'log', mode=0700)
		self.VARDIR = constructPath(self.HOMEDIR, 'var', mode=0700)
		self.ETCDIR = constructPath(self.HOMEDIR, 'etc', mode=0700)
		self.TOOLDIR = constructPath(self.HOMEDIR, 'tools', mode=0700)
		self.LIBDIR = constructPath(self.HOMEDIR, 'lib', mode=0700)
		self.PRIVKEYDIR = constructPath(self.HOMEDIR, 'privkeys', mode=0700)
		self.PUBKEYDIR = constructPath(self.HOMEDIR, 'pubkeys', mode=0700)

	def setPidFileVar(self):
		self.PIDFILE = os.path.join(self.VARDIR, 'toolserver.pid')

	def append(self, title, **vars):
		self._sections.append((title, vars.keys()))
		for k in vars.keys():
			setattr(self, k, vars[k])

	def sections(self):
		return self._sections

	def write(self, filename):
		cfg = open(filename, 'w')
		for (sec, keys) in self.sections():
			for line in sec.split('\n'):
				cfg.write('# %s\n' % line)
			for k in keys:
				cfg.write('%s=%s\n' % (k, repr(config[k])))
			cfg.write('\n')
		cfg.close()

# compute some special filenames and paths
try: 
	HOMEDIR = os.environ['TOOLSERVER_HOME']
except KeyError: 
	if sys.platform == 'win32': 
		try: 
			home = os.environ['HOME'] # for custom environments
		except KeyError: # maybe default NT/2K/XP install
			try: home = os.environ['APPDATA'] # should be user specific and not the profile
			except KeyError:
				try: home = os.environ['USERPROFILE'] # should be user specific
				except KeyError:
					home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
	else: 
		home = os.environ['HOME']
	HOMEDIR = constructPath(home, '.Toolserver', mode=0700)

# set up the config dispatcher object
config = SystemConfiguration(PREFIX, HOMEDIR)

config.append("how is your server called?",
	serverhostname = 'localhost',
	serverip = '127.0.0.1',
	serverport = 4334
)

config.append("""should the monitor server be started? If yes, set monitorport
to something different than 0 and add a monitor password.
The monitor will run on serverip.""",
	monitorport = 0,
	monitorpassword = ''
)

config.append("character encoding used for document data",
	documentEncoding = 'iso-8859-1'
)

config.append("these are switches that are set by tsctl",
	daemon = 1,
	verbose = 0,
	debugrpc = 0,
	contract = 0,
	basicauth = 0,
	autoreload = 0
)

config.append("""this activates simplification of SOAP arguments
to python base types. This slows down processing
a lot (due to recursive traversal of all parameters),
but allows easier migration of existing code.""",
	simplify = 0
)

config.append("this sets the default timeout for socket communication",
	timeout = 30
)

config.append("""these values are for managing worker threads dynamically.
they are usefull for a moderate load. minfreeworkers says
how much workers must be free as a minimum (checked every
freecheckinterval seconds), maxfreeworkers says how much workers
should be free as a maximum and startfreeworkers says how much
workers should be started when there are less than minfreeworkers
free workers. If maxfreeworkers is bigger than minfreeworkers,
the number of running workers will never fall below maxfreeworkers.""",
	freecheckinterval = 5,
	minfreeworkers = 4,
	maxfreeworkers = 6,
	startfreeworkers = 4,
	maxworkers = 100
)

config.append("these values are for managing transient tool caches",
	maxage = 300,
	maxitems = 1000
)

if hasCrypto:
	config.append("""activating PickleRPC should only be done if you can trust
all systems that can connect to your server or you took security measures to
protect yourself from unpickling exploits! If you enable the PickleRPC
protocol, you must enable RSA authentication, too. PickleRPC traffic
is encrypted by session keys that themselves are encrypted using RSA.""",
		allowpicklerpc = 0
	)

if hasCrypto:
	config.append("""You can activate RSA authentication for RPC calls. If you
do, you need to generate keys of a given keysize and need to store all
allowed public keys in your pubkeys directory where they are checked
automatically. The keys need to be stored under the servername of the
toolservers (or actually clients) calling.""",
		rsakeysize = 1024,
		rsaauthenticate = 0
	)

