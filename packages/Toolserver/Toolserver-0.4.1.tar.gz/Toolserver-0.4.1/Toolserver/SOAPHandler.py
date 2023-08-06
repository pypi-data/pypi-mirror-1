# -*- Mode: Python -*-

# soap_handler is a SOAP handler for medusa built on xmlrpc_handler
#
# this adaption was done by Georg Bauer <bauer@gws.ms>

# See http://www.xml-rpc.com/
#     http://www.pythonware.com/products/xmlrpc/

# Based on "xmlrpcserver.py" by Fredrik Lundh (fredrik@pythonware.com)

import SOAPpy

from SOAPpy.Types import simplify

from Toolserver.Config import config
from Toolserver.RPCHandler import rpc_handler, registerRPCHandler

# patch a new characters method into SOAPParser that converts to
# system ecoding. This is a hack, but SOAPpy doesn't support passing
# encodings to the parser and Toolserver internal stuff doesn't work well
# with unicode.
def characters(self, c):
	""" adds chars from a string only in system encoding """
	if self._data != None:
		self._data += c.encode(config.documentEncoding)

SOAPpy.SOAPParser.characters = characters

# patch a new dump_string into SOAPBuilder for the same reason
def dump_string(self, obj, tag, typed = 0, ns_map = {}):
	""" delivers chars from a string only in latin-1 encoding """
	import cgi

	tag = tag or self.gentag()

	id = self.checkref(obj, tag, ns_map)
	if id == None:
		return
	
	try: data = obj._marshalData()
	except: data = obj

	if type(data) != type(u''):
		data = data.decode(config.documentEncoding)
	
	self.out.append(self.dumper(None, "string", cgi.escape(data), tag,
		typed, ns_map, self.genroot(ns_map), id))

SOAPpy.SOAPBuilder.dump_string = dump_string
SOAPpy.SOAPBuilder.dump_str = dump_string
SOAPpy.SOAPBuilder.dump_unicode = dump_string

class soap_handler(rpc_handler):

	_prefix = 'SOAP'
	_name = 'SOAPpy'

	def simplify_value(self, value):
		return simplify(value)

	def parse_request(self, data, request):
		(r, header, body, attrs) = SOAPpy.parseSOAPRPC(
			data, header=1, body=1, attrs=1
		)
		method = r._name
		args = r._aslist()
		kw = r._asdict()
		kwnames = r._keyord
		return (args, kw, kwnames, method)

	def build_exception(self, request, excinfo, reason):
		(e, d, tb) = excinfo
		f = SOAPpy.faultType('%s:Client' % SOAPpy.NS.ENV_T, e)
		f._setDetail(str(d))
		return SOAPpy.buildSOAP(f, encoding=config.documentEncoding)

	def build_result(self, request, method, result):
		return SOAPpy.buildSOAP(
			kw = {'%sResponse' % method: result},
			encoding=config.documentEncoding
		)

registerRPCHandler(soap_handler)
