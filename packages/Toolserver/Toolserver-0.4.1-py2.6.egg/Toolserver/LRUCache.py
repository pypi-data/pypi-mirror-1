"""

Toolserver Framework for Python - LRU dictionary

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
import weakref
import threading

from Toolserver.Config import config
from Toolserver.Worker import dispatcher
from Toolserver.Utils import logInfo, logWarning, logError

# This class manages a dictionary item
class LRUItem:

	def __init__(self, key, value):
		self.key = key
		self.value = value
		self.time = time.time()
	
	def getValue(self):
		self.time = time.time()
		return self.value
	
	def __cmp__(self, other):
		return cmp(self.time, other.time)

# This class manages a dictionary whose content
# is only kept for a given maximum age. Every access
# to items reset's their age.
class LRUDictionary:

	def __init__(self, tool, name, maxage=300,  maxitems=1000):
		self.name = name
		self.tool = weakref.proxy(tool)
		self.maxage = maxage
		self.maxitems = 1000
		self.sync = threading.Condition()
		self.handler = None
		self.dict = {}

	# This method manages the LRU algorihm
	def lruloop(self, *args):
		try:
			self.sync.acquire()
			self.handler = threading.currentThread()
			logWarning('starting LRU manager thread for %s:%s', '.'.join(self.tool.name), self.name)
			while self.dict and self.handler and self.handler._running and dispatcher.running:
				self.sync.wait(5)
				l = filter(lambda el, reftime=time.time() - self.maxage: el.time < reftime, self.dict.values())
				for el in l:
					del self.dict[el.key]
				if len(self.dict) > self.maxitems:
					l = self.dict.values()
					l.sort()
					for el in l[:-self.maxitems]:
						del self.dict[el.key]
		finally:
			self.handler = None
			self.sync.release()
			logWarning('stopping LRU manager thread for %s:%s', '.'.join(self.tool.name), self.name)
		return (self.tool, '<LRUDictionary %s>' % self.name)

	def keys(self):
		return self.dict.keys()
	
	def values(self):
		return self.dict.values()

	def items(self):
		return self.dict.items()
	
	def has_key(self, key):
		return self.dict.has_key(key)

	def __getitem__(self, key):
		try:
			self.sync.acquire()
			item = self.dict[key]
			value = item.getValue()
			try: return weakref.proxy(value)
			except: return value
		finally: self.sync.release()

	def __setitem__(self, key, value):
		if self.handler is None:
			dispatcher.append(self.tool, self.lruloop, None, None)
		try:
			self.sync.acquire()
			item = LRUItem(key, value)
			self.dict[key] = item
			self.sync.notify()
		finally: self.sync.release()

	def __delitem__(self, key, value):
		try:
			self.sync.acquire()
			del self.dict[key]
		finally: self.sync.release()

