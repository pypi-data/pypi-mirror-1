"""

Toolserver Framework for Python - XML-RPC Introspection

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

import time

from Toolserver.Config import config
from Toolserver.Tool import registerTool, StandardTool, getTools, getTool
from Toolserver.Utils import parseQueryFromRequest, parseQueryFromString, ForbiddenError, quote
from Toolserver.Utils import format, formatSource

class SystemTool(StandardTool):

	"""
	This tool allows introspection of available webservice methods.
	It implements all three methods from the system namespace.
	"""

	# These are type declarations for WSDL generation. If you refer to
	# types you define yourself, use the typens: namespace. If you refer
	# to system defined types, use the xsd: namespace!
	_types = StandardTool._types + (
		('stringArray', ['xsd:string']),
	)

	def listMethods(self):
		"""
		This method returns a list of all registered methods of
		the webservice. This collects all methods from all registered
		tools. Only registered tools are returned, not transient
		tools!
		"""
		liste = []
		for tool in getTools():
			for method in tool.listRegisteredFunctions():
				liste.append('.'.join(tool.name)+'.'+method)
		return liste

	listMethods_signature = ('typens:stringArray')

	def _resolveType(self, tool, typesig):
		for (typ, typdef) in getattr(tool, '_types'):
			if typ == typesig:
				if type(typdef) == type(''):
					if typdef.startswith('xsd:'):
						return typdef
					elif typdef.startswith('typens:'):
						return self._resolveType(tool, typdef)
					else: raise ValueError(typdef)
				else:
					return typdef
		raise ValueError(typ)
	
	def methodSignature(self, method):
		"""
		This returns a list of method signatures for a given method.
		Since TooFPy only allows for one signature due to restrictions
		of the SOAP WSDL generator, this method only returns that
		signature transformed in a one-element array. XML-RPC
		type specs are guessed from the SOAP type specs. Simple
		types are from the WSDL xsd: namespace, so they might contain
		tag names that are not known to standard XML-RPC clients.
		"""
		namespace = method.split('.')
		method = namespace[-1]
		namespace = namespace[:-1]
		tool = getTool(namespace)
		if hasattr(tool, '%s_signature' % method):
			soapsig = getattr(tool, '%s_signature' % method)
			signature = []
			for sig in soapsig:
				typespec = None
				if sig.startswith('xsd:'):
					typespec = sig[4:]
				elif sig.startswith('typens:'):
					typesig = self._resolveType(tool, sig)
					if type(typesig) == (type('')):
						typespec = typesig[4:]
					elif type(typesig) == type([]):
						typespec = 'array'
					elif type(typesig) == type({}):
						typespec = 'struct'
				if typespec:
					signature.append(typespec)
				else:
					raise ValueError(sig)
			return [signature]
		else:
			return []
	
	methodSignature_signature = ('typens:stringArray', 'xsd:string')

	def methodSignature_pre_condition(self, method):
		assert type(method) == type(''), 'method must be a string'
	
	def methodSignature_post_condition(self, result):
		assert type(result) == type([]), 'result must be an array'
		for row in result:
			assert type(row) == type([]), 'result must be an array of arrays'

	def methodHelp(self, method):
		"""
		This method returns the documentation string for a
		specific method. It adds source from pre- and post-
		conditions, too.
		"""
		namespace = method.split('.')
		method = namespace[-1]
		namespace = namespace[:-1]
		tool = getTool(namespace)
		precond = getattr(tool, method+'_pre_condition', None)
		postcond = getattr(tool, method+'_post_condition', None)
		method = getattr(tool, method)
		fdoc = format(method.__doc__)
		if precond or postcond:
			fdoc += '<dl>'
			if precond:
				fdoc += '<dt>Pre-Condition</dt><dd>%s</dd>' % formatSource(precond)
			if postcond:
				fdoc += '<dt>Post-Condition</dt><dd>%s</dd>' % formatSource(postcond)
			fdoc += '</dl>'
		return fdoc

	def methodHelp_pre_condition(self, method):
		assert type(method) == type(''), 'method must be a string'
	
	def methodHelp_post_condition(self, result):
		assert type(result) == type(''), 'result must be a string'

registerTool(SystemTool, 'system')

