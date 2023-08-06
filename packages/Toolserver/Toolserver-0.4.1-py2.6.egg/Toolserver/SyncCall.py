"""

Tool Server Framework - execute a call synchronously

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

import sys
import traceback

from Toolserver.Config import config
from Toolserver.Context import context
from Toolserver.Utils import logWarning, logError, ForbiddenError, AuthError, Apply, validateWrapper, shortenModuleFile
from Toolserver.Tool import hasTool, getTool

def _apply(tool, method, validated, args, kw):
	"""
	This function calls a tools method with full wrapping enabled (much
	as it would be called via RPC). You can decide wether you want full
	authentication checking (validated=1) or wether you don't need
	it (validated=0). Usually you will call either vapply or nvapply
	defined below. You can either pass in a fully qualified method (set
	tool to None) or a already resolved tool and a tool-relative method
	spec.
	"""

	base = None
	if tool is None:
		parts = method.split('.')
		base = parts[:-1]
		method = parts[-1]

	if method.find('_') >= 0:
		raise ForbiddenError(method)

	if tool or hasTool(base):
		if tool is None:
			tool = getTool(base)
		if hasattr(tool, method):
			try:
				context._begin()
				context.request = request
				try:
					tool._begin()
					meth = getattr(tool, method)
					if validated and validateWrapper('LOCAL', tool, method, orderedargs, kw):
						raise ForbiddenError('IPC')
					fr = Apply(tool, method, meth, args, kw)

				except:
					tool._abort()
					raise
				else:
					tool._commit()
			finally:
				context._end()
		else:
			raise AttributeError('Tool %s has no method %s' % (tool.name, method))
	else:
		raise AttributeError('There is no tool at %s' % map(lambda s: str(s), base))

	return fr

def nvapply(method, *args, **kw):
	"""
	Shorthand to call without validation (and with automatic parameter
	packing). The method must be a fully qualified method name.
	"""
	return _apply(None, method, 0, args, kw)

def vapply(method, *args, **kw):
	"""
	Shorthand to call with validation (and with automatic parameter
	packing). The method must be a fully qualified method name.
	"""
	return _apply(None, method, 1, args, kw)

class ToolProxyMethod:
	"""
	This is a wrapper that handles method delegation
	"""
	
	def __init__(self, tool, name, validated):
		self._tool = tool
		self._method = name
		self._validated = validated
	
	def __call__(self, *args, **kw):
		if self._validated:
			return _apply(self._tool, self._method, 0, args, kw)
		else:
			return _apply(self._tool, self._method, 1, args, kw)

class ToolProxy:
	"""
	This class builds a proxy around a tool that automatically
	delegates method calls to the tool via nvapply or vapply,
	depending on the validated switch.
	"""

	def __init__(self, tool, validated=0):
		self._tool = getTool(tool)
		self._validated = validated
	
	def __nonzero__(self):
		return 1
	
	def __getattr__(self, name):
		if self._tool.hasmethod(name):
			return ToolProxyMethod(self._tool, name, self._validated)
		else:
			raise AttributeError(name)

def getToolProxy(name, validated=0):
	"""
	Alternative to getTool that returns a ToolProxy instead of a
	direct tool. This tool proxy automatically uses all wrappers as
	if the method was called from the outside.
	"""
	return ToolProxy(name, validated)

