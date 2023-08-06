"""

Toolserver Framework for Python - reactor chains

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
import copy
import types
import asyncore

from Toolserver.Context import context
from Toolserver.Utils import logInfo, logWarning, logError

class ChainContext:

	"""
	This class represents the running context of a chain reaction.
	This is to encapsulate special values per chain reaction run.
	Especially the chain status is copied to prevent problems
	from the chain of handlers changing while a chain reaction
	takes place.

	A speciality of reactor chains is that exceptions while
	processing with a single handler will get noticed, but the
	chain will under all circumstances run through and produce some
	result. Non-working handlers will just be skipped.

	The chain is run in it's own local context, so handlers can pass
	on stuff via the context to other instances. Of course this breaks
	decoupling. There are predefined context variables:

	context.chain - the current running chain (actually only the name)
	context.history - a list of historic values
	"""

	def __init__(self, chain):
		self.handlers = copy.copy(chain.handlers)
		self.chain = chain.name

	def run(self, value, acceptable=None):
		try:
			context._begin()
			context.chain = self.chain
			context.history = []
			for handler in self.handlers:
				v = copy.copy(value)
				try:
					nv = handler(v)
					if nv is None:
						raise ValueError('None not allowed in reactor chains')
					elif acceptable is not None and not acceptable(value):
						raise ValueError('%s is no acceptable value in this chain run' % nv)
					else:
						value = nv
				except:
					(file, fun, line), t, v, tbinfo = asyncore.compact_traceback()
					logError('exception in trigger thunk: (%s:%s %s)', t, v, tbinfo)
				else:
					context.history.append(v)
			return value
		finally: context._end()

class ReactorChain:
	"""
	Reactor chains are abstract method handlers of tools that are
	chained together. They can be thought of as abstract events that
	get passed along a result that every step in the chain is allowed
	to modify until the last chain reactor handled the element. All
	Tools need to know about what this element is, of course - so they
	are usually highly coupled with regard to this element, but not with
	regard to their inner workings and communications.

	Usually a chain is installed by a Tool. It installs it and hooks
	up it's own handler for events on that chain. It runs the chain
	with one value and uses the resulting value for whatever it needs
	to do. Other tools can hook either preprocessing (addHead) or
	postprocessing (addTail) handlers into the chain.

	If you don't set up any handlers in advance, the run method will
	be an identity function - the passed in value will be returned
	directly. This allows you to set up hooks for other tools that
	needn't be hooked and won't take up too much resources when noone
	hooks to them.
	"""
	
	def __init__(self, name):
		self.name = name
		self.handlers = []

	def getHandler(self, handlerspec):
		"""
		A class must either implement a special handler for the
		chain with a name _on_<chainname> where each dot in the
		chain name is replaced by an underscore or must implement
		a global event handler _on. This handler must take one
		parameter, the value (actually it takes two parameters, as
		the first one will be self).

		An alternative to an instance would be a function object
		or a callable.
		"""
		if type(handlerspec) == types.InstanceType:
			name = '_on_%s' % self.name.replace('.', '_')
			if hasattr(handlerspec, name):
				return getattr(handlerspec, name)
			elif hasattr(handlerspec, '_on'):
				return getattr(handlerspec, '_on')
			else:
				raise AttributeError(name)
		elif type(handlerspec) == types.LambdaType:
			return handlerspec
		elif hasattr(handlerspec, '__call__'):
			return handlerspec
		raise TypeError(handlerspec)

	def addHead(self, handler):
		"""
		Add a handler to the head of the chain. The name should
		be a dotted namespace notation.
		"""
		self.handlers.insert(0, self.getHandler(handler))
	
	def addTail(self, handler):
		"""
		Add a handler to the tail of the chain. The name should
		be a dotted namespace notation.
		"""
		self.handlers.append(self.getHandler(handler))

	def run(self, value, acceptable=None):
		"""
		If there are any handlers, build a chain context and
		run the chain. If there are no handlers, just return
		the value itself. acceptable can be a callable that
		checks wether a value is acceptable to the chain.
		"""
		if len(self.handlers):
			return ChainContext(self).run(value, acceptable=acceptable)
		else:
			return value

chains = {}

def getChain(name):
	"""
	Returns either a new ReactorChain or an already existing ReactorChain
	to hook yourself to or to run with some value.
	"""
	assert type(name) == type(''), 'chain name must be a string'
	if not chains.has_key(name):
		chains[name] = ReactorChain(name)
	return chains[name]

def runChain(name, value, acceptable=None):
	"""
	Runs the named chain with the given value. Just syntactic sugar
	for chain resolving and running. You can pass in a callable
	to acceptable that is called on every iteration and checks wether
	a value is acceptable. If not, the step will be skipped.
	"""
	return getChain(name).run(value, acceptable=acceptable)

def addChainHead(name, handler):
	"""
	adds some handler to the head of a chain. Just syntactic sugar.
	"""
	getChain(name).addHead(handler)

def addChainTail(name, handler):
	"""
	adds some handler to the tail of a chain. Just syntactic sugar.
	"""
	getChain(name).addTail(handler)

