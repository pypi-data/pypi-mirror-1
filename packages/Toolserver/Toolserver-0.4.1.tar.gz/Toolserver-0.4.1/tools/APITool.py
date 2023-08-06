"""

Toolserver Framework for Python - API documentation generation

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
import traceback

from Toolserver.Tool import StandardTool, registerTool, getTools, getTool
from Toolserver.Factory import FactoryTool, TransientFactoryTool
from Toolserver.RPCHandler import getRegisteredRPCHandlers
from Toolserver.Config import config
from Toolserver.Utils import quote, format, document, formatSource

def getwrapper(tool, method, qualifier):
	l = []
	meth = method+'_'+qualifier
	for el in dir(tool):
		if el.startswith(meth):
			p = el.split('_')
			if len(p) == 3:
				l.append((p[-1], getattr(tool, el).__doc__ or ''))
			elif len(p) == 2:
				l.append(('Default', getattr(tool, el).__doc__ or ''))
	return l

def getDocumentation(namespace):
	tool = getTool(namespace)
	toolname = '.'.join(tool.name)

	doc = '<h1>class %s:</h1>' % tool.__class__.__name__
	doc += '<p>'+format(tool.__class__.__doc__)
	doc += '<p>The following URLs can be used with this tool.'
	doc += '<dl>'
	doc += '<dt>http://%s:%s/API/%s</dt><dd>this API documentation</dd>' % (
		config.serverhostname, config.serverport, '/'.join(tool.name)
	)
	doc += '<dt>http://%s:%s/WSDL/%s</dt><dd>the WSDL for this tool</dd>' % (
		config.serverhostname, config.serverport, '/'.join(tool.name)
	)
	for thehandler in getRegisteredRPCHandlers():
		doc += '<dt>http://%s:%s/%s/%s</dt><dd>the %s connection point for this tool</dd>' % (
			config.serverhostname, config.serverport, thehandler._prefix, '/'.join(tool.name), thehandler._name
		)
	doc += '<dt>http://%s:%s/%s/</dt><dd>the REST connection base for this tool</dd>' % (
		config.serverhostname, config.serverport, '/'.join(tool.name)
	)
	doc += '</dl>'
	if hasattr(tool, '_invariant'):
		doc += '<h2>Tool Invariant</h2>'
		doc += '%s' % formatSource(getattr(tool, '_invariant'))
	if hasattr(tool, '_error') or hasattr(tool, '_parser') or hasattr(tool, '_generator'):
		doc += '<h2>Tool Level REST Wrapper</h2>'
		doc += '<dl>'
		if hasattr(tool, '_error'): doc += '<dt>Error Reporter</dt><dd>'+format(tool._error.__doc__)+'</dd>'
		if hasattr(tool, '_parser'): doc += '<dt>Parser</dt><dd>'+format(tool._parser.__doc__)+'</dd>'
		if hasattr(tool, '_generator'): doc += '<dt>Generator</dt><dd>'+format(tool._generator.__doc__)+'</dd>'
		doc += '</dl>'
	doc += '<h2>Defined Methods</h2>'
	doc += '<blockquote>'
	lst = []
	for el in dir(tool):
		if el.find('_') < 0:
			attr = getattr(tool, el)
			if hasattr(attr, 'im_func'):
				func = attr.im_func
				if hasattr(func, 'func_code'):
					code = func.func_code
					fdoc = '<dt>def %s(%s):</dt><dd>%s</dd>' % (
						code.co_name,
						', '.join(code.co_varnames[1:code.co_argcount]),
						format(attr.__doc__)
					)
					precond = getattr(tool, el+'_pre_condition', None)
					postcond = getattr(tool, el+'_post_condition', None)
					parser = getwrapper(tool, el, 'parser')
					generator = getwrapper(tool, el, 'generator')
					error = getwrapper(tool, el, 'error')
					if precond or postcond or parser or generator:
						fdoc += '<dd><dl>'
						if precond:
							fdoc += '<dt>Pre-Condition</dt><dd>%s</dd>' % formatSource(precond)
						if postcond:
							fdoc += '<dt>Post-Condition</dt><dd>%s</dd>' % formatSource(postcond)
						if parser or generator or error:
							fdoc += '<dt>REST API Wrapper</dt><dd><dl>'
							for (m, d) in parser:
								fdoc += '<dt>%s Parser</dt><dd>%s</dd>' % (m, d)
							for (m, d) in generator:
								fdoc += '<dt>%s Generator</dt><dd>%s</dd>' % (m, d)
							for (m, d) in error:
								fdoc += '<dt>%s Error Reporter</dt><dd>%s</dd>' % (m, d)
							fdoc += '</dl></dd>'
						fdoc += '</dl></dd>'
					lst.append((code.co_name, fdoc))
	lst.sort(lambda a,b: cmp(a[0], b[0]))
	doc += '<dl>'
	doc += ''.join(map(lambda a: a[1], lst))
	doc += '</dl>'
	doc += '</blockquote>'

	return document('Documentation for Namespace %s' % '.'.join(namespace), doc)

class APISubTool(TransientFactoryTool):
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
		return getDocumentation(self.name[1:])

# patch the factory class (can't be defined, because it's circular)
APISubTool.FactoryClass = APISubTool

class APIMainTool(FactoryTool):

	"""
	This is the main documentation tool. This tool manages the access
	to automatically generated documentation for installed tools.
	"""

	FactoryClass = APISubTool
	_content_type = 'text/html'

	def _keys(self):
		liste = []
		for tool in getTools():
			if tool.name and tool.name[0] not in liste:
				liste.append(tool.name[0])
		return liste

	def index_validate_RPC(self, *args, **kw):
		raise ForbiddenError('No RPC')

	def index(self, request, data):
		"""
		This method just builds the list of installed tools. It
		should be accessed directly with a web browser. No RPC access
		is possible.
		"""

		doc = '<h1>List of installed namespaces</h1>'
		doc += '<p>Here is a list of installed tools and their namespaces'
		doc += '<dl>'
		for tool in getTools():
			doc += '<dt><a href="/API%s">%s</a></dt>' % (
				tool.uri, '.'.join(tool.name)
			)
			doc += '<dd>%s</dd>' % format(
				tool.__class__.__doc__
			)
		doc += '</dl>'
		return document('List of installed namespaces', doc)

registerTool(APIMainTool, 'API')

