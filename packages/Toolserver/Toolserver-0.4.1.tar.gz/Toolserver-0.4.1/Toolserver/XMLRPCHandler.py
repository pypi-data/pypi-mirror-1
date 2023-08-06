# -*- Mode: Python -*-

# xmlrpc_handler is a XMLRPC handler for medusa built on xmlrpc_handler
#
# this adaption was done by Georg Bauer <bauer@gws.ms>

# See http://www.xml-rpc.com/
#     http://www.pythonware.com/products/xmlrpc/

# Based on "xmlrpcserver.py" by Fredrik Lundh (fredrik@pythonware.com)

import xmlrpclib

from Toolserver.RPCHandler import rpc_handler, registerRPCHandler
from Toolserver.Config import config

class xmlrpc_handler(rpc_handler):

	_prefix = 'RPC2'
	_name = 'XMLRPC'

	def parse_request(self, data, request):
		p, u = xmlrpclib.getparser()
		u._encoding = config.documentEncoding
		p.feed(data)
		p.close()
		args = u.close()
		method = u.getmethodname()
		return (args, {}, [], method)

	def build_exception(self, request, excinfo, reason):
		(e, d, tb) = excinfo
		code = -32400
		if reason == 'method.unknown':
			code = -32601
		elif reason == 'method':
			code = -32500
		f = xmlrpclib.Fault(code, '%s: %s' % (e, d))
		return xmlrpclib.dumps(f, methodresponse=1, encoding=config.documentEncoding)

	def build_result(self, request, method, result):
		if result is None: result = ''
		return xmlrpclib.dumps((result,), methodresponse=1, encoding=config.documentEncoding)

registerRPCHandler(xmlrpc_handler)
