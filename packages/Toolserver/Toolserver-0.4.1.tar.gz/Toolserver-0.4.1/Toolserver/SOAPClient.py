"""Toolserver Framework for Python - SOAP client code

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

import SOAPpy

from SOAPpy.Types import simplify

from Toolserver.ClientRegistry import registerClient
from Toolserver.ClientMachinery import AbstractClient, documentEncoding

# patch a new characters method into SOAPParser that converts to
# system ecoding. This is a hack, but SOAPpy doesn't support passing
# encodings to the parser and Toolserver internal stuff doesn't work well
# with unicode.
def characters(self, c):
	""" adds chars from a string only in system encoding """
	if self._data != None:
		self._data += c.encode(documentEncoding)

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
		data = data.decode(documentEncoding)
	
	self.out.append(self.dumper(None, "string", cgi.escape(data), tag,
		typed, ns_map, self.genroot(ns_map), id))

SOAPpy.SOAPBuilder.dump_string = dump_string
SOAPpy.SOAPBuilder.dump_str = dump_string
SOAPpy.SOAPBuilder.dump_unicode = dump_string

class SOAPClient(AbstractClient):

	_prefix = 'SOAP'
	_name = 'SOAPpy'

	def simplify_value(self, value):
		return simplify(value)

	def is_exception(self, value):
		return isinstance(value, SOAPpy.faultType)

	def build_request(self, method, args, kw):
		return SOAPpy.buildSOAP(
			args = args, kw = kw, method=method,
			encoding=documentEncoding
		)

	def parse_response(self, data, obj):
		(p, attrs) = SOAPpy.parseSOAPRPC(data, attrs=1)
		return p

registerClient(SOAPClient, 'url')

