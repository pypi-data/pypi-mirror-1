"""
Toolserver Framework for Python - client for PickleRPC

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

try:
	from Crypto.Cipher import Blowfish
	hasCrypto = 1
except ImportError: hasCrypto = 0

from base64 import decodestring, encodestring
from zlib import compress, decompress

try: from cPickle import dumps, loads
except: from pickle import dumps, loads

from Toolserver.ClientRegistry import registerClient
from Toolserver.ClientMachinery import AbstractClient, documentEncoding

class Stuff:

	def __init__(self, srv, gen=1):
		if gen:
			srv._randpool.stir()
			self.secret = srv._randpool.get_bytes(16)
			srv._randpool.stir()

class PickleRPCClient(AbstractClient):

	_prefix = 'PYRPC'
	_name = 'PickleRPC'
	_mimetype = 'text/plain'
	_already_compressed = 1

	def __init__(self, *args, **kw):
		AbstractClient.__init__(self, *args, **kw)
		self.privkey = getattr(self._srv, 'privkey', 1)
		self.pubkey = getattr(self._srv, 'pubkey', 1)

	def build_request(self, method, args, kw):
		obj = Stuff(self._srv)
		data = dumps((method, args, kw))
		data = compress(data)
		b = Blowfish.new(obj.secret, Blowfish.MODE_CBC)
		data = b.encrypt(data+' '*(8-len(data)%8))
		data = encodestring(data)
		return (data, obj)

	def output_header_hook(self, request, data, obj):
		key = self.pubkey.encrypt(obj.secret, '')
		key = encodestring(key[0]).strip().replace('\n','')
		request.putheader("X-PickleRPC-Secret", key)

	def parse_response(self, data, obj):
		data = decodestring(data)
		b = Blowfish.new(obj.secret, Blowfish.MODE_CBC)
		data = b.decrypt(data)
		data = decompress(data)
		data = loads(data)
		return data

	def input_header_hook(self, headers, data):
		res = Stuff(self._srv, 0)
		key = headers.getheader('X-PickleRPC-Secret')
		key = (decodestring(key),)
		key = self.privkey.decrypt(key)
		res.secret = key
		return res

if hasCrypto:
	registerClient(PickleRPCClient, 'url', 'privkey', 'pubkey', 'localname')

