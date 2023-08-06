"""

Toolserver Framework for Python - Tool Factories

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

import weakref

from Toolserver.Config import config
from Toolserver.Context import context
from Toolserver.Tool import StandardTool
from Toolserver.LRUCache import LRUDictionary

def weakproxy(obj):
	if type(obj) == weakref.ProxyType:
		return obj
	else:
		return weakref.proxy(obj)

class TransientTool(StandardTool):

	"""
	This class implements transient tools. Transient tools
	are not automatically registered at startup, but are later
	instantiated by a factory tool. The transient tool shares
	part of the factories instance variables to reduce
	resource usage by default.

	This is the abstract class - either you instantiated an
	abstract class, or the programmer forgot to give a meaningfull
	description.
	"""

	def __init__(self, subid, factory, **kw):
		StandardTool.__init__(self, factory.name + (str(subid),), **kw)
		self._subid = subid
		self._my_factory = weakproxy(factory)

	# Queues are shared with the factory tool to minimize
	# resource usage.
	def _initqueues(self, **kw):
		self._timer = weakproxy(self._my_factory._timer)
		self._queue = weakproxy(self._my_factory._queue)

	# The following methods are delegated to the factory. If you
	# want to handle them on transient tool level, just
	# overload them. Usually the cursor is handled on the
	# factory level, though.
	def _begin(self):
		return self._my_factory._begin()
	
	def _abort(self):
		return self._my_factory._abort()
	
	def _commit(self):
		return self._my_factory._commit()
	
class FactoryTool(StandardTool):

	"""
	This class implements a factory tool. A factory tool lives
	in the middle of the path - the path element after it's own
	path is used to dynamically instantiate a transient tool.

	This is the abstract class - either you instantiated an
	abstract class, or the programmer forgot to give a meaningfull
	description.
	"""

	# Subclasses might want to use their own overloaded
	# factory class or just use the default one
	FactoryClass = TransientTool

	def __init__(self, name, **kw):
		StandardTool.__init__(self, name, **kw)
		self._factory = 1
	
	def _initqueues(self, maxage=config.maxage, maxitems=config.maxitems, **kw):
		StandardTool._initqueues(self, **kw)
		self._cache = LRUDictionary(self, 'cache', maxage=maxage, maxitems=maxitems)

	# This method checks wether a subid is valid in the
	# context of this factory. It uses the keys method
	# to check wether a given subid is in the
	# list of valid keys. You can overload it if you
	# work with large keyspaces.
	def has_key(self, subid):
		if subid in self._keys(): return 1
		else: return 0

	# This method should be overloaded to return a list
	# of valid keys for sub tools. This method starts with an
	# underscore so it isn't exported automatically.
	def _keys(self):
		raise NotImplemented
	
	# This method should return a transient tool that is based
	# on this factory and the passed subid. All additional
	# parameters to the factory are passed to the transient tool.
	# Only weak references are returned, so don't store those
	# references for too long!
	def __getitem__(self, subid):
		subname = self.name + (subid,)
		if not self.has_key(subid):
			raise KeyError(subname)
		try: return self._cache[subname]
		except KeyError:
			tool = self.FactoryClass(subid, self, **self._options)
			try:
				context._begin()
				tool._initdb(**tool._options)
				tool._initqueues(**tool._options)
				try:
					tool._begin()
					tool._initopts(**tool._options)
				except:
					tool._abort()
					return None
				else:
					tool._commit()
			finally: context._end()
			self._cache[subname] = tool
			return weakproxy(tool)

class TransientFactoryTool(TransientTool, FactoryTool):

	"""
	This class implement transient factories. Due to the recursive
	nature of the getTool implementation, you can have factories
	that dynamically create other factories that themselves can
	create factories or transient tools. Transient factories share
	the factory cache of the parent factory.

	This is the abstract class - either you instantiated an
	abstract class, or the programmer forgot to give a meaningfull
	description.
	"""

	def __init__(self, subid, factory, **kw):
		TransientTool.__init__(self, subid, factory, **kw)
		self._factory = 1

	def _initqueues(self, **kw):
		TransientTool._initqueues(self, **kw)
		self._cache = self._my_factory._cache

