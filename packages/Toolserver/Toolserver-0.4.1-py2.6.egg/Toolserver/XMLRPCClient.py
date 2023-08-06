"""Toolserver Framework for Python - XMLRPC client code

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

import xmlrpclib

from Toolserver.ClientRegistry import registerClient
from Toolserver.ClientMachinery import AbstractClient, documentEncoding

class XMLRPCClient(AbstractClient):

	_prefix = 'RPC2'
	_name = 'XMLRPC'

	def simplify_value(self, value):
		return simplify(value)

	def is_exception(self, value):
		return isinstance(value, xmlrpclib.Fault)

	def build_request(self, method, args, kw):
		return xmlrpclib.dumps(args, method, encoding=documentEncoding)

	def parse_response(self, data, obj):
		(p, u) = xmlrpclib.getparser()
		u._encoding = documentEncoding
		p.feed(data)
		p.close()
		res = u.close()
		if len(res) == 1:
			res = res[0]
		return res

registerClient(XMLRPCClient, 'url')

