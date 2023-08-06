"""
Toolserver Framework for Python - client machinery for remote tools

Copyright (c) 2002, Georg Bauer <gb@rfc1437.de>, except where the file
explicitly names other copyright holders and licenses.

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
import urllib
import httplib

try:
	from Crypto.Hash import SHA256
	from Crypto.Util.randpool import RandomPool
	hasCrypto = 1
except ImportError: hasCrypto = 0

from base64 import decodestring, encodestring
from zlib import decompress

try: from cPickle import load, dumps, loads
except: from pickle import load, dumps, loads

from Toolserver.ClientRegistry import protocols

# the default document encoding
documentEncoding = 'iso-8859-1'

urlre = re.compile(r'^(https?)://([a-zA-Z0-9\-\.]*)(:[0-9]*)?(/.*)$')

class Method:

	def __init__(self, name, client):
		self._name = name
		self._client = client

	def __str__(self):
		return '<Toolserver.Client.Method %s on %s>' % (self._name, self._client._url)

	def __getattr__(self, name):
		return Method(self._name + '.' + name, self._client)

	def _rsaheaders(self, r, data):
		if hasCrypto and self._client._srv.privkey and self._client._srv.localname:
			crc = SHA256.new()
			crc.update(data)
			hash = crc.hexdigest()
			signature = self._client._srv.privkey.sign(hash, '')
			signature = str(signature[0])
			r.putheader("X-TooFPy-Hash", hash)
			r.putheader("X-TooFPy-Signature", signature)
			r.putheader("X-TooFPy-Signer", self._client._srv.localname)

	def __call__(self, *args, **kw):
		data = self._client.build_request(self._name, args, kw)
		obj = None
		if type(data) == type(()):
			obj = data[1]
			data = data[0]
		r = self._client.connect()
		self._client.output_header_hook(r, data, obj)
		self._rsaheaders(r, data)
		if not self._client._already_compressed:
			r.putheader("Accept-encoding", 'deflate')
		r.putheader("Content-length", str(len(data)))
		r.endheaders()
		r.send(data)
		code, msg, headers = r.getreply()
		if code == 401:
			sendheaders = []
			wwwauth = headers.getheader("WWW-Authenticate").split()
			if wwwauth[0] == 'Basic':
				if hasattr(self._client._srv, 'basic'):
					sendheaders.append(("Authorization", 'Basic %s' % encodestring('%s:%s' % self._client._srv.basic)))
				else:
					raise ValueError('No credentials for basic auth available')
			else:
				raise ValueError('Auth method %s not supported' % wwwauth[0])
			r = self._client.connect()
			self._client.output_header_hook(r, data, obj)
			self._rsaheaders(r, data)
			for (header, value) in sendheaders:
				r.putheader(header, value)
			r.putheader("Content-length", str(len(data)))
			r.endheaders()
			r.send(data)
			code, msg, headers = r.getreply()
		if code < 200 or code > 299:
			raise ValueError(msg)
		data = r.getfile().read()
		content_encoding = headers.getheader("Content-encoding")
		if content_encoding == 'deflate':
			data = decompress(data)
		obj = self._client.input_header_hook(headers, data)
		if hasCrypto and self._client._srv.pubkey:
			hash = headers.getheader("X-TooFPy-Hash")
		 	signature = headers.getheader("X-TooFPy-Signature")
			if not hash or not signature:
				raise ValueError("either hash or signature not provided (or both)")
			signature = (long(signature),)
			if not self._client._srv.pubkey.verify(hash, signature):
				raise ValueError("signature can't be verified")
			crc = SHA256.new()
			crc.update(data)
			if crc.hexdigest() != hash:
				raise ValueError("hash can't be verified")
		res = self._client.parse_response(data, obj)
		if self._client._srv.simplify:
			res = self._client.simplify_value(res)
		encryption = headers.getheader('X-PickleRPC-Encryption')
		if self._client.is_exception(res): raise res
		else: return res

class AbstractClient:

	_prefix = 'AbstractRPC'
	_name = 'Abstract RPC Client'
	_mimetype = 'text/xml'
	_already_compressed = 0

	def __init__(self, srv, url, *args):
		self._srv = srv
		m = urlre.match(url)
		assert m, "Wrong format for URL - only http/https allowed"
		self._proto = m.group(1)
		assert self._proto in ('http', 'https'), "Only http and https allowed"
		self._host = m.group(2)
		if self._proto == 'http':
			self._port = 80
		elif self._proto == 'https':
			self._port = 443
		if m.group(3):
			self._port = int(m.group(3)[1:])
		self._path = m.group(4)
		self._proxyhost = getattr(self._srv, 'proxyhost', None)
		self._proxyport = getattr(self._srv, 'proxyport', None)

	def __str__(self):
		return '<%s Client>' % self._prefix

	def connect(self):
		path = self._path
		if self._proxyhost:
			r = httplib.HTTP(self._proxyhost)
			path = self._url
		elif self._proto == 'https':
			r = httplib.HTTPS(self._host, self._port)
		elif self._proto == 'http':
			r = httplib.HTTP(self._host, self._port)
		r.putrequest("POST", path)
		r.putheader("Host", self._host)
		r.putheader("User-agent", "TooFPy %s Client" % self._name)
		r.putheader("Content-type", self._mimetype)
		return r

	def __getattr__(self, name):	
		return Method(name, self)

	def simplify_value(self, value):
		return value

	def is_exception(self, value):
		return isinstance(value, Exception)

	def build_request(self, method, args, kw):	
		raise NotImplemented()

	def parse_response(self, data, obj):
		raise NotImplemented()

	def output_header_hook(self, request, data, obj):
		pass

	def input_header_hook(self, headers, data):
		return None

class RemoteToolserver:

	"""
	This class factors out the connection handling for remote tools
	and the used protocol. Just instantiate a RemoteToolserver instance
	and fetch tool proxies with the getTool method. Typical keywords
	are proxyhost and proxyport to specify the proxy or secret to specify
	a shared secret for protocols relying on this. Another one is simplify,
	which can be used to simplify results of calls (especially usefull
	for SOAP). It's default is off. If you want to use RSA authentication
	you can specify privkey and pubkey to point to files where your private
	key and the public key of the server reside. You need to specify the
	localname option, too. If you want to use basic authentication, set
	the option basic to a tuple (user, password).
	"""

	def __init__(self, baseurl, protocol, **kw):
		assert protocols.has_key(protocol), 'unknown protocol '+protocol
		if hasCrypto:
			self._randpool = RandomPool(500)
		self._baseurl = baseurl
		while self._baseurl and self._baseurl.endswith('/'):
			self._baseurl = self._baseurl[:-1]
		self._protocol = protocol
		if kw.has_key('pubkey'):
			kw['pubkey'] = load(open(kw['pubkey']))
		else: kw['pubkey'] = None
		if kw.has_key('privkey'):
			kw['privkey'] = load(open(kw['privkey']))
		else: kw['privkey'] = None
		self.simplify = 0
		self.localname = ''
		for k in kw.keys():
			setattr(self, k, kw[k])

	def getTool(self, path, protocol=''):
		"""
		This builds a proxy for a remote tool. You can override the
		protocol name if the server uses different access points than
		you use.
		"""
		if not protocol: protocol = self._protocol
		if type(path) in (type(''), type(u'')):
			path = path.split('.')
		assert type(path) in (type(()), type([])), 'path must be either string or sequence'
		self.url = "%s/%s/%s" % (
			self._baseurl, protocol,
			'/'.join(path)
		)
		r = protocols[protocol]
		args = []
		for i in range(1,len(r)):
			args.append(getattr(self, r[i]))
		return r[0](self, *args)

