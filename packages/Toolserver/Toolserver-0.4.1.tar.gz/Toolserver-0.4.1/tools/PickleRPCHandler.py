# -*- Mode: Python -*-

# pickle_handler is a RPC handler for medusa built on xmlrpc_handler that
# uses base64 encoded pickles instead of XML
#
# this adaption was done by Georg Bauer <bauer@gws.ms>

# See http://www.xml-rpc.com/
#     http://www.pythonware.com/products/xmlrpc/

# Based on "xmlrpcserver.py" by Fredrik Lundh (fredrik@pythonware.com)

from base64 import encodestring, decodestring
try: from cPickle import dumps, loads
except ImportError: from pickle import dumps, loads

from zlib import compress, decompress

from Toolserver.Config import config, hasCrypto
from Toolserver.RPCHandler import rpc_handler, registerRPCHandler
from Toolserver.Authentication import privatekeys, publickeys
from Toolserver.Utils import logWarning, ForbiddenError

randompool = None
if hasCrypto:
	from Crypto.Cipher import Blowfish
	from Crypto.Util.randpool import RandomPool
	randompool = RandomPool(500)

def genPassword():
	randompool.stir()
	secret = randompool.get_bytes(16)
	randompool.stir()
	return secret

class pickle_handler(rpc_handler):

	_prefix = 'PYRPC'
	_name = 'PickleRPC'
	_mime_type = 'text/plain'

	def parse_request(self, data, request):
		key = request.get_header('X-PickleRPC-Secret')
		key = (decodestring(key),)
		key = privatekeys[config.serverhostname].decrypt(key)
		s = decodestring(data)
		b = Blowfish.new(key, Blowfish.MODE_CBC)
		s = b.decrypt(s)
		s = decompress(s)
		(method, args, kw) = loads(s)
		if not hasattr(request, '_my_secret'):
			request._my_secret = genPassword()
		return (args, kw, kw.keys(), method)

	def build_exception(self, request, excinfo, reason):
		(e, d, tb) = excinfo
		res = dumps(d, 1)
		res = compress(res)
		if not hasattr(request, '_my_secret'):
			request._my_secret = genPassword()
		b = Blowfish.new(request._my_secret, Blowfish.MODE_CBC)
		res = b.encrypt(res+' '*(8-len(res)%8))
		return encodestring(res)

	def build_result(self, request, method, result):
		res = dumps(result, 1)
		res = compress(res)
		if not hasattr(request, '_my_secret'):
			request._my_secret = genPassword()
		b = Blowfish.new(request._my_secret, Blowfish.MODE_CBC)
		res = b.encrypt(res+' '*(8-len(res)%8))
		return encodestring(res)

	def outgoing_header_hook(self, request, data):
		key = publickeys[request.get_header('X-TooFPy-Signer')].encrypt(request._my_secret, '')
		key = key[0]
		key = encodestring(key).strip().replace('\n','')
		request['X-PickleRPC-Secret'] = key

if hasCrypto and config.allowpicklerpc and config.rsaauthenticate:
	registerRPCHandler(pickle_handler)

