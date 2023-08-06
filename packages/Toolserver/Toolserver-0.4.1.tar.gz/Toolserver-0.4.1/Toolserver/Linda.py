"""

Toolserver Framework for Python - Linda like tuple spaces

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

import copy
import time
import types
import weakref
import threading

from Toolserver.Config import config
from Toolserver.Worker import dispatcher
from Toolserver.ReactorChain import runChain

class Matcher:
	"""
	Matcher match tuples agains patterns. A pattern is a tuple of
	classes, functions, types and non-classes intermixed. Classes and Types
	are matched with isinstance, non-classes are matched with ==, functions
	are matched by applying them to the element and using the return value
	as a boolean. A matcher can only match tuples of the same size as
	the pattern - other tuples are allways regarded as non-matching.
	"""

	classtypes = (types.TypeType, types.ClassType)
	functiontypes = (types.BuiltinFunctionType, types.BuiltinMethodType, types.FunctionType, types.MethodType)

	def __init__(self, pattern):
		self.constants = []
		self.classes = []
		self.functions = []
		self.ref = 0L
		self.len = len(pattern)
		self.pattern = pattern
		idx = 0
		for pat in pattern:
			if type(pat) in self.classtypes:
				self.classes.append((idx, pat))
			elif type(pat) in self.functiontypes:
				self.functions.append((idx, pat))
			else:
				self.constants.append((idx, pat))
			idx += 1
	
	def match(self, tuple):
		if len(tuple) != self.len:
			return 0
		for (idx, pat) in self.constants:
			if tuple[idx] != pat:
				return 0
		for (idx, pat) in self.classes:
			if not isinstance(tuple[idx], pat):
				return 0
		for (idx, pat) in self.functions:
			if not pat(tuple[idx]):
				return 0
		return 1

class TupleSpace:

	"""
	Tuple spaces are bags of tuples of different length with elements
	of different types. Tuples are put in as constant values. They
	will be deep-copied to prevent structure sharing. They can be pulled
	out with patterns. Patterns are actually lists of classes, functions,
	types and constants intermixed. The match is done with class Matcher.
	Tuplespaces can have a defined lifetime for tuples - if that lifetime
	is set, tuples will drop out of the space, even if nobody requested
	them.
	"""

	def __init__(self, lifetime=0):
		self.space = []
		self.purgetime = []
		self.sync = threading.Condition()
		self.ref = 0L
		self.lifetime = lifetime
	
	def _out(self, lifetime, tuple):
		now = time.time()
		purgetime = 0
		if lifetime > 0:
			purgetime = now + lifetime
		self.ref += 1
		l = len(tuple)
		tuple = copy.deepcopy(tuple)
		while len(self.space) <= l:
			self.space.append([])
			self.purgetime.append(0)
		self.space[l].append((self.ref, purgetime, tuple, {}))
		if purgetime:
			if self.purgetime[l]:
				self.purgetime[l] = min(purgetime, self.purgetime[l])
			else:
				self.purgetime[l] = purgetime
		if self.purgetime[l] and self.purgetime[l] < now:
			newpurgetime = 0
			idx = 0
			todel = []
			for (ref, purgetime, tuple, seen) in self.space[l]:
				if purgetime > 0:
					if purgetime < now:
						todel.append(idx)
					else:
						if newpurgetime:
							newpurgetime = min(purgetime, newpurgetime)
						else:
							newpurgetime = purgetime
				idx += 1
			todel.reverse()
			for idx in todel:
				runChain('system.linda.delete', self.space[l][idx])
				del self.space[l][idx]
			self.purgetime[l] = newpurgetime

	def outLimited(self, lifetime, tupl):
		"""
		This method stores a tuple with limited lifetime
		in the tuplespace, where the lifetime in seconds differs
		from the default tuplespace lifetime!
		"""
		try:
			self.sync.acquire()
			self._out(lifetime, tuple(tupl))
			self.sync.notify()
		finally:
			self.sync.release()

	def out(self, tupl):
		"""
		This method stores a tuple in the tuplespace and
		sends out a notify to any possible waiters. Tuples
		are deepcopied to prohibit structure sharing.
		"""
		try:
			self.sync.acquire()
			self._out(self.lifetime, tuple(tupl))
			self.sync.notify()
		finally:
			self.sync.release()
	
	def _in(self, matcher, seenid):
		now = time.time()
		l = matcher.len
		if len(self.space) > l:
			space = self.space[l]
			idx = 0
			todel = []
			try:
				for (ref, purgetime, tuple, seen) in space:
					if purgetime > 0 and purgetime < now:
						todel.append(idx)
					elif seenid and seen.has_key(seenid):
						pass
					elif matcher.ref < ref and matcher.match(tuple):
						if seenid: seen[seenid] = 1
						else: todel.append(idx)
						return tuple
					idx += 1
			finally:
				todel.reverse()
				for idx in todel:
					del self.space[l][idx]
		matcher.ref = self.ref
		raise KeyError('This tuplespace has no element that matches %s' % repr(matcher.pattern))

	def inNoWait(self, pattern):
		"""
		This method returns the first tuple that matches
		the given pattern. The matched tuple is removed from
		the tuplespace. If the tuple is not available, a
		KeyError is raised.
		"""
		matcher = Matcher(pattern)
		try:
			self.sync.acquire()
			return self._in(matcher, None)
		finally:
			self.sync.release()

	def inWait(self, timeout, pattern):
		"""
		This method returns the first tuple that matches the given
		pattern. The matched tuple is removed from the tuplespace. If
		the tuple is not available,  the call will wait. If the central
		dispatcher is shut down, the in call will raise a KeyError.
		You can give a timeout on how long you want to wait. The
		default is 5 minutes. If the timeout strikes, the call
		will raise a KeyError.
		"""
		matcher = Matcher(pattern)
		if not timeout:
			timeout = 300
		try:
			self.sync.acquire()
			try: return self._in(matcher, None)
			except KeyError: pass
			then = time.time() + timeout
			while dispatcher.running and then > time.time():
				self.sync.wait(5)
				if dispatcher.running:
					try: return self._in(matcher, None)
					except KeyError: pass
			return self._in(matcher)
		finally:
			self.sync.release()

	def keepNoWait(self, seenid, pattern):
		"""
		This differes from inNoWait in that it keeps the
		tuple in the tuplespace. The tuple is noted as seen
		and so only visited once. This is usefull for broadcast
		types of notifications. Keep is best combined with
		time-limited tuples, as that will keep the tuplespace
		small.
		"""
		matcher = Matcher(pattern)
		try:
			self.sync.acquire()
			return self._in(matcher, seenid)
		finally:
			self.sync.release()

	def keepWait(self, timeout, seenid, pattern):
		"""
		This differs from inWait in that it keeps the
		tuple in tuplespace as keepNoWait does.
		"""
		matcher = Matcher(pattern)
		if not timeout:
			timeout = 300
		try:
			self.sync.acquire()
			try: return self._in(matcher, seenid)
			except KeyError: pass
			then = time.time() + timeout
			while dispatcher.running and then > time.time():
				self.sync.wait(5)
				if dispatcher.running:
					try: return self._in(matcher, seenid)
					except KeyError: pass
			return self._in(matcher, seenid)
		finally:
			self.sync.release()

class MetaTupleSpace(TupleSpace):

	"""
	This tuplespace class adds metadata to single tuples. The metadata
	is stored as an additional tuple element and is removed from the
	tuple on return. It's actually just a convenience wrapper around
	the standard tuplespace class where out methods get an additional
	parameter and in/keep methods return an additional value (actually
	they return a tuple of the original tuple and the original metadata).
	Usually metadata is transferred into the tuplespace as a dictionary,
	but any type should do just fine.
	"""

	def outLimited(self, lifetime, tupl, meta):
		try:
			self.sync.acquire()
			self._out(lifetime, tuple(tupl)+(meta,))
			self.sync.notify()
		finally:
			self.sync.release()

	def out(self, tupl, meta):
		try:
			self.sync.acquire()
			self._out(self.lifetime, tuple(tupl)+(meta,))
			self.sync.notify()
		finally:
			self.sync.release()
	
	def inNoWait(self, pattern):
		tuple = TupleSpace.inNoWait(self, pattern)
		return (tuple[:-1], tuple[-1])

	def inWait(self, timeout, pattern):
		tuple = TupleSpace.inWait(self, timeout, pattern)
		return (tuple[:-1], tuple[-1])

	def keepNoWait(self, seenid, pattern):
		tuple = TupleSpace.keepNoWait(self, seenid, pattern)
		return (tuple[:-1], tuple[-1])

	def keepWait(self, timeout, seenid, pattern):
		tuple = TupleSpace.keepNoWait(self, timeout, seenid, pattern)
		return (tuple[:-1], tuple[-1])

# Set up a default tuple space for use in this toolserver instance.
# This standard universe (tuple space) has unlimited default lifetime.
universe = TupleSpace()
