"""

Toolserver Framework for Python - WSDL generation

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
import sys
import inspect
import traceback

from Toolserver.Tool import StandardTool, registerTool, getTools, getTool
from Toolserver.Factory import FactoryTool, TransientFactoryTool
from Toolserver.Config import config
from Toolserver.Utils import StringIO, format, document

def getWSDL(namespace):
	response = ''
	tool = getTool(namespace)
	toolname = ''.join(map(lambda e: e.capitalize(), namespace))
	types = []
	if hasattr(tool, '_types'):
		for (typ, sig) in tool._types:
			if type(sig) == type([]):
				elements = []
				for k in sig:
					elements.append(
						'<xsd:attribute ref="soapenc:arrayType" wsdl:arrayType="%s[]"/>' % k
					)
				types.append('\n'.join((
					'<xsd:complexType name="%s">' % typ,
					'<xsd:complexContent>',
					'<xsd:restriction base="soapenc:Array">',
					'\n'.join(elements),
					'</xsd:restriction>',
					'</xsd:complexContent>',
					'</xsd:complexType>'
				)))
			elif type(sig) == type({}):
				elements = []
				for k in sig.keys():
					elements.append(
						'<xsd:element name="%s" type="%s"/>' % (
							k, sig[k]
						)
					)
				types.append('\n'.join((
					'<xsd:complexType name="%s">' % typ,
					'<xsd:all>',
					'\n'.join(elements),
					'</xsd:all>',
					'</xsd:complexType>'
				)))
	messages = []
	operations = []
	opnames = []

	for el in filter(lambda e: e.find('_') < 0, dir(tool)):
		attr = getattr(tool, el)
		if hasattr(attr, 'im_func') and hasattr(attr.im_func, 'func_code'):
			func = attr.im_func
			code = func.func_code
			parms = code.co_varnames[1:code.co_argcount]
			sig = []
			ret = 'xsd:anyType'
			if hasattr(tool, '%s_signature' % el):
				sig = list(getattr(tool, '%s_signature' % el))
				ret = sig[0]
				del sig[0]
			lst = []
			for p in parms:
				t = 'xsd:anyType'
				if len(sig):
					t = sig[0]
					del sig[0]
				lst.append('<part name="%s" type="%s"/>' % (p, t))
			if len(lst):
				messages.append('\n'.join((
					'<message name="%sRequest">' % el,
					'\n'.join(lst),
					'</message>'
				)))
			else: messages.append('<message name="%sRequest"/>' % el)
			messages.append('\n'.join((
				'<message name="%sResponse">' % el,
				'<part name="return" type="%s"/>' % ret,
				'</message>'
			)))
			operations.append('\n'.join((
				'<operation name="%s">' % el,
				'<input message="typens:%sRequest"/>' % el,
				'<output message="typens:%sResponse"/>' % el,
				'</operation>'
			)))
			opnames.append(el)

	response += '<?xml version="1.0"?>\n'
	response += '<definitions name="%s"\n' % toolname
	response += '\ttargetNamespace="urn:%s"\n' % toolname
	response += '\txmlns:typens="urn:%s"\n' % toolname
	response += '\txmlns:xsd="http://www.w3.org/2001/XMLSchema"\n'
	response += '\txmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"\n'
	response += '\txmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/"\n'
	response += '\txmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"\n'
	response += '\txmlns="http://schemas.xmlsoap.org/wsdl/">\n'
	if len(types):
		response += '\n<types>\n'
		response += '<xsd:schema xmlns="http://www.w3.org/2001/XMLSchema"\n'
		response += '\ttargetNamespace="urn:%s">\n\n' % toolname
		response += '\n'.join(types)
		response += '\n\n</xsd:schema>\n'
		response += '\n</types>\n\n'
	response += '\n'.join(messages)
	response += '\n\n<portType name="%sPort">\n' % toolname
	response += '\n'.join(operations)
	response += '\n</portType>\n'
	response += '\n<binding name="%sBinding" type="%sPort">\n' % (toolname, toolname)
	response += '<soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>\n'
	for op in opnames:
		response += '<operation name="%s">\n' % op
		response += '<soap:operation soapAction="urn:%sAction"/>' % toolname
		response += '<input>\n'
		response += '<soap:body use="encoded"\n'
		response += '\tnamespace="urn:%s"\n' % toolname
		response += '\tencodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>\n'
		response += '</input>\n'
		response += '<output>\n'
		response += '<soap:body use="encoded"\n'
		response += '\tnamespace="urn:%s"\n' % toolname
		response += '\tencodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>\n'
		response += '</output>\n'
		response += '</operation>\n'
	response += '\n</binding>\n\n'
	response += '<service name="%sService">\n' % toolname
	response += '<port name="%sPort" binding="typens:%sBinding">\n' % (toolname, toolname)
	response += '<soap:address location="http://%s:%s/SOAP/%s"/>\n' % (
		config.serverhostname, config.serverport,
		'/'.join(namespace)
	)
	response += '</port>\n'
	response += '</service>\n'
	response += '\n</definitions>\n'

	return response

class wsdl_handler:

	def __init__(self):
		self._callcounter = 0
		self._errorcounter = 0
		self._shortcounter = 0
		self._calls = {}

	def status(self):
		return producers.lines_producer([
			'<li>%s' % html_repr(self),
			'<ul>',
			'<li><b>Total Calls:</b> %d' % (self._callcounter + self._errorcounter + self._shortcounter),
			'<li><b>WSDLs requested for:</b> %s' % (', '.join(
				map(lambda e: '%s (%d)' % (e, self._calls[e]), self._calls.keys())
			) or 'None so far'),
			'<li><b>Calls with suppressed delivery:</b> %d' % self._shortcounter,
			'<li><b>Calls with Errors:</b> %d' % self._errorcounter,
			'</li>'
			'</ul>',
		])

	def match (self, request):
		if request.command in ('GET', 'HEAD') and request.uri.startswith('/WSDL/'):
			return 1
		else:
			return 0

	def handle_request (self, request):
		dispatcher.append(self, continue_request, StringIO(''), request)

class WSDLSubTool(TransientFactoryTool):
	"""
	This tool returns the documentation of a tool whose name is
	exactly like this one, just without the first path element.
	"""

	_content_type = 'text/html'

	def _isSubTool(self, tool):
		return len(tool.name) > (len(self.name)-1) and self.name[1:] == tool.name[:len(self.name)-1]

	def _keys(self):
		liste = []
		for tool in getTools():
			if self._isSubTool(tool):
				if len(tool.name) >= len(self.name) and tool.name[len(self.name)-1] not in liste:
					liste.append(tool.name[len(self.name)-1])
		return liste

	def index_validate_RPC(self, *args, **kw):
		raise ForbiddenError('No RPC')

	def index(self, request, data):
		return getWSDL(self.name[1:])

# patch the factory class (can't be defined, because it's circular)
WSDLSubTool.FactoryClass = WSDLSubTool

class WSDLMainTool(FactoryTool):

	"""
	This is the main documentation tool. This tool manages the access
	to automatically generated documentation for installed tools.
	"""

	FactoryClass = WSDLSubTool
	_content_type = 'text/xml'

	def _keys(self):
		liste = []
		for tool in getTools():
			if tool.name and tool.name[0] not in liste:
				liste.append(tool.name[0])
		return liste

	index_content_type = 'text/html'

	def index_validate_RPC(self, *args, **kw):
		raise ForbiddenError('No RPC')

	def index(self, request, data):
		"""
		This method just builds the list of installed tools. It
		should be accessed directly with a web browser. No RPC access
		is possible.
		"""

		doc = '<h1>List of installed WSDLs</h1>'
		doc += '<p>Here is a list of installed tools and their WSDL URIs'
		doc += '<dl>'
		for tool in getTools():
			doc += '<dt><a href="/WSDL%s">%s</a></dt>' % (
				tool.uri, '.'.join(tool.name)
			)
			doc += '<dd>%s</dd>' % format(
				tool.__class__.__doc__
			)
		doc += '</dl>'
		return document('List of installed WSDLs', doc)

registerTool(WSDLMainTool, 'WSDL')

