# -*- Mode: Python -*-

# xmlrpc_handler is a XMLRPC handler for medusa built on xmlrpc_handler
#
# This handler uses the much faster py-xmlrpc library. You have to first
# install it from http://sourceforge.net/projects/py-xmlrpc/
# This handler currently is untested, as I don't have py-xmlrpc installed.
#
# this adaption was done by Georg Bauer <bauer@gws.ms>

# See http://www.xml-rpc.com/
#     http://www.pythonware.com/products/xmlrpc/

# Based on "xmlrpcserver.py" by Fredrik Lundh (fredrik@pythonware.com)

import pyxmlrpclib

from Toolserver.RPCHandler import rpc_handler, registerRPCHandler
from Toolserver.Config import config

class py_xmlrpc_handler(rpc_handler):

	_prefix = 'PYRPC2'
	_name = 'PY-XMLRPC'

	def parse_request(self, data, request):
		p, u = pyxmlrpclib.getparser()
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
		f = pyxmlrpclib.Fault(code, '%s: %s' % (e, d))
		return pyxmlrpclib.dumps(f, methodresponse=1, encoding=config.documentEncoding)

	def build_result(self, request, method, result):
		if result is None: result = ''
		return pyxmlrpclib.dumps((result,), methodresponse=1, encoding=config.documentEncoding)

registerRPCHandler(py_xmlrpc_handler)
