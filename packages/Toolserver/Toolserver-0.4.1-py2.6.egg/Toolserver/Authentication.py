"""

Toolserver Framework for Python - Authentication handling code

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

import re
import os
import glob
from base64 import decodestring
from threading import RLock

from medusa import http_server

try: from cPickle import load
except ImportError: from pickle import load

try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO

from Toolserver.Config import config, hasCrypto
from Toolserver.Utils import logInfo, AuthError, ForbiddenError
from Toolserver.Tool import StandardTool

if hasCrypto:
	from Crypto.Hash import SHA256

class KeyHash:

	def __init__(self, typ, path):
		self.typ = typ
		self.path = path
		self.hash = {}
		self.time = {}
		self.lock = RLock()

	def has_key(self, name):
		keypath = os.path.join(self.path, '%s.key' % name)
		return os.path.exists(keypath)

	def __getitem__(self, name):
		keypath = os.path.join(self.path, '%s.key' % name)
		if os.path.exists(keypath):
			if self.hash.has_key(name):
				if os.stat(keypath)[8] > self.time[name]:
					self.loadKey(name, keypath)
			else:
				self.loadKey(name, keypath)
		else:
			if self.hash.has_key(name):
				try:
					self.lock.acquire()
					del self.hash[name]
					del self.time[name]
				finally:
					self.lock.release()
		return self.hash[name]

	def get(self, name, default=None):
		try: return self[name]
		except KeyError: return default

	def loadKey(self, name, path):
		logInfo("Loading RSA key for %s", name)
		try:
			self.lock.acquire()
			self.hash[name] = load(open(path))
			self.time[name] = os.stat(path)[8]
		finally:
			self.lock.release()

publickeys = KeyHash('public', config.PUBKEYDIR)
privatekeys = KeyHash('private', config.PRIVKEYDIR)

class SingleFileHash:

	def __init__(self, name):
		self.hash = {}
		self.time = 0
		self.name = name
		self.path = os.path.join(config.ETCDIR, self.name)
		self.lock = RLock()

	def has_key(self, key):
		if os.path.exists(self.path):
			if os.stat(self.path)[8] > self.time:
				self.load()
			return self.hash.has_key(key)
		else: return 0

	def __getitem__(self, key):
		if os.path.exists(self.path):
			if os.stat(self.path)[8] > self.time:
				self.load()
		return self.hash[key]
	
	def get(self, key, default=None):
		try: return self[key]
		except KeyError: return default

	def load(self):
		self.log()
		if os.path.exists(self.path):
			hash = {}
			for line in open(self.path).readlines():
				line = line.strip()
				if line and not line.startswith('#') and line.find(':')>0:
					(p1, p2) = line.split(':',1)
					self.parse(hash, p1.strip(), p2.strip())
			try:
				self.lock.acquire()
				self.hash = hash
				self.time = os.stat(self.path)[8]
			finally:
				self.lock.release()

class HostHash(SingleFileHash):

	def log(self):
		logInfo("Loading host infos from %s", self.name)

	def parse(self, hash, client, ip):
		hash[ip] = client

hostsallow = HostHash('hosts.allow')
hostsdeny = HostHash('hosts.deny')

class PasswordHash(SingleFileHash):

	def log(self):
		logInfo("Loading passwd infos")

	def parse(self, hash, user, password):
		hash[user] = password

passwd = PasswordHash('passwd')

class GroupsHash(SingleFileHash):

	def log(self):
		logInfo("Loading clientgroups from groups")

	def parse(self, hash, group, users):
		users = map(lambda e: e.strip(), users.split(','))
		for user in users:
			if not hash.has_key(user):
				hash[user] = []
			hash[user].append(group)

usergroups = GroupsHash('groups')

class EtcAuthenticator:
	"""
	This is a simple authenticator that uses the above globals to
	check authentication. The validate method just returns the
	authenticated user, his groups and his permissions.
	"""

	def validate(self, realm, user, password):
		global passwd
		if passwd.get(user, None) == password:
			return (user, usergroups.get(client, []))
		else:
			raise AuthError(realm)
	
# instantiate the right form of authenticator
authenticator = EtcAuthenticator()

# This function checks a request for authentication contents and
# returns the client and the groups of this client.
# Authentication is optional - if no headers are in there, the variables will
# be set to None and [] respectively. Tools will have to check themselves
# if they want to be sure they have correct authentication. Use the attached
# AuthenticatedTool base class for your tools if you don't want to bother
# too much with this. If there are authentication headers, they must match -
# if they don't, an exception is raised. If RSA authentication is enabled,
# it is obligatory - if you don't provide RSA authentication headers, an
# error is raised. If other authentication methods trigger, they all must
# evaluate to a correct validation. If any method triggers a forbidden or
# authentication error, an exception is raised.

def checkAuthentication(request, data, realm, checkrsa=1):
	if hostsdeny.has_key(request.channel.addr[0]):
		raise ForbiddenError('listed in hosts.deny')
	client = hostsallow.get(request.channel.addr[0], None)
	groups = usergroups.get(client, [])
	authheader = request.get_header('Authorization')
	authmethod = None
	if client: authmethod = 'X-IP'
	if authheader:
		authparts = authheader.split()
		if authparts[0].lower() == 'basic':
			authmethod = 'Basic'
			(auser, apass) = decodestring(authparts[1]).split(':',1)
			(client, groups) = authenticator.validate(realm, auser, apass)
		else:
			raise ValueError('unknown auth method: %s' % authparts[0])
	if client: logInfo('%s is identified as client %s(%s)',
		request.channel.addr[0], client,
		','.join(groups))
	if hasCrypto and config.rsaauthenticate and checkrsa:
		authmethod = 'X-RSA'
		hash = request.get_header('X-TooFPy-Hash')
		signature = request.get_header('X-TooFPy-Signature')
		client = request.get_header('X-TooFPy-Signer')
		if not hash or not signature or not client:
			raise ForbiddenError('missing auth headers')
		if not publickeys.has_key(client):
			raise ForbiddenError('you are not know to me')
		signature = (long(signature),)
		if not publickeys[client].verify(hash, signature):
			raise ForbiddenError("signature doesn't verify")
		crc = SHA256.new()
		crc.update(data)
		if crc.hexdigest() != hash:
			raise ForbiddenError("hash doesn't verify")
		groups = usergroups.get(client, [])
	return (authmethod, client, groups)

# This function generates the authentication headers based for HTTP auth
def generateAuthentication(request, realm):
	request['WWW-Authenticate'] = 'Basic realm="%s@%s"' % (
		realm, config.serverhostname
	)

# This function generates the authentication headers for RSA auth
def generateRSAAuthentication(request, response):
	if hasCrypto and config.rsaauthenticate and privatekeys.has_key(config.serverhostname):
		crc = SHA256.new()
		crc.update(response)
		hash = crc.hexdigest()
		signature = privatekeys[config.serverhostname].sign(hash, '')
		signature = str(signature[0])
		request['X-TooFPy-Hash'] = hash
		request['X-TooFPy-Signature'] = signature
		request['X-TooFPy-Signer'] = config.serverhostname

class AuthenticatedTool(StandardTool):
	"""
	This tool is a base tool for usage when authentication is important.
	It just implements standard validation wrappers that can be overridden
	if you want different handling. It introduces two new class variables:
	_groups and _clients. Validation checks agains these two variables.
	They can be either a string or a list of strings. If they are a string
	and the string is '*', every client or group matches. If they are
	a string other than '*', the named group or named client matches. If
	they are a list of strings, one of the given strings must match the
	given client or groups. Authentication is used for both RPC and REST
	style access in the same way. This is different from the above two
	classes where only RPC style access is handled and REST style access
	is actively forbidden. Usually this is the best class to base your
	tool on if you want to use authentication - even if you only want to
	be sure that later addition of authentication is mostly painless. Out
	of the box this class will behave exactly like StandardTool, it just
	adds one layer of protection.

	This is an abstract class, either the author didn't subclass it or
	didn't bother to define her own documentation string.
	"""

	_groups = '*'
	_clients = '*'

	def _check_groups(self):
		if self._groups == '*':
			return ''
		elif type(self._groups) in (type(''), type(u'')):
			if self._groups in context.groups:
				return ''
		elif type(self._groups) in (type(()), type([])):
			for group in context.groups:
				if group in self._groups:
					return ''
		else:
			raise TypeError(self._groups)
		return self._realm
				
	def _check_clients(self):
		if self._clients == '*':
			return ''
		elif type(self._clients) in (type(''), type(u'')):
			if self._clients == context.client:
				return ''
		elif type(self._clients) in (type(()), type([])):
			if context.client in self._clients:
				return ''
		else:
			raise TypeError(self._clients)
		return self._realm

	def _validate(self, request):
		return self._check_groups() or self._check_clients()

	def _validate_HTTP(self, request, parts):
		return self._check_groups() or self._check_clients()

	def _validate_RPC(self, *args, **kw):
		return self._check_groups() or self._check_clients()

