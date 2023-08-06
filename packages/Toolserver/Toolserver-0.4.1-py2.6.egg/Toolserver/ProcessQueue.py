"""

Toolserver Framework for Python - processing queues

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
from Toolserver.AsyncCall import async_call, createAsyncId, checkAsyncIdRunning
from Toolserver.Utils import logWarning, logInfo, logError

# a single queue event
class QueueEvent:

	def __init__(self, asyncid, specifier, keepresult, tool, queue, method, args, kw):
		self.asyncid = asyncid
		self.specifier = specifier
		self.keepresult = keepresult
		self.tool = tool
		self.queue = weakref.proxy(queue)
		self.method = method
		self.args = args
		self.kw = kw
	
	# This method may need to be overridden to make
	# the queue sortable.
	def __cmp__(self, other):
		raise NotImplementedError
	
	# This method needs to be overridden to enable the
	# processor loop to select wether this element
	# of the queue should be processed now.
	def processNow(self):
		raise NotImplementedError
	
	# This method calls the event function synchronously, using
	# the async_call wrapper to manage result capturing correctly.
	def call(self):
		async_call(
			None,
			self.tool,
			(self.args, self.kw, self.asyncid, self.keepresult),
			self.method
		)

	# This method calls the event function asynchronously
	def async(self):
		dispatcher.append(
			self.tool,
			async_call,
			(self.args, self.kw, self.asyncid, self.keepresult),
			self.method
		)

# This event class manages timer events that are sorted by
# their due time.
class TimerEvent(QueueEvent):
	
	def __cmp__(self, other):
		return -1*cmp(self.specifier, other.specifier)
	
	def processNow(self):
		return time.time() > self.specifier

# This event class manages priority events that are sorted by
# their priority and creation time. The specifier is a
# tuple of both.
class PriorityEvent(QueueEvent):

	def __cmp__(self, other):
		return (
			cmp(self.specifier[0], other.specifier[0]) or
			-1*cmp(self.specifier[1], other.specifier[1])
		)
	
	def processNow(self):
		return 1

# a queue for method calls. Uses the given EventClass for
# events. Usually doesn't need overriding.
class ProcessingQueue:

	def __init__(self, tool, name, EventClass, sync=1):
		self.name = name
		self.tool = weakref.proxy(tool)
		self.sync = sync
		self.queue = []
		self.queueregistry = {}
		self.queuesync = threading.Condition()
		self.queuehandler = None
		self.EventClass = EventClass
	
	# This method manages queue events. Events are handled in a queue
	# with one worker thread working on this one queue and triggering
	# method calls. This method is appended to the dispatcher to
	# process events from this queue.
	def eventloop(self, *args):
		try:
			self.queuesync.acquire()
			self.queuehandler = threading.currentThread()
			logInfo('starting queue thread for %s:%s', '.'.join(self.tool.name), self.name)
			while len(self.queue) and self.queuehandler._running and dispatcher.running:
				self.queuesync.wait(5)
				if len(self.queue) and dispatcher.running and self.queuehandler._running and self.queue[0].processNow():
					logInfo('processing events for %s:%s', '.'.join(self.tool.name), self.name)
					while dispatcher.running and self.queuehandler._running and len(self.queue):
						event = self.queue[0]
						del self.queueregistry[event.asyncid]
						del self.queue[0]
						if self.sync:
							try:
								self.queuesync.release()
								event.call()
							finally:
								self.queuesync.acquire()
						else: event.async()
		finally:
			self.queuehandler = None
			self.queuesync.release()
			logInfo('stopping queue thread for %s:%s', '.'.join(self.tool.name), self.name)
		return (self.tool, '<ProcessingQueue %s>' % self.name)

	# Add a queued call. The specifier is used to order or select queued
	# events on processing time. You can decide wether you need
	# the result or not.
	def queueCall(self, specifier, method, keepresult, args, kw):
		if self.queuehandler is None:
			dispatcher.append(self.tool, self.eventloop, None, None)
		try:
			self.queuesync.acquire()
			asyncid = createAsyncId(self)
			event = self.EventClass(asyncid, specifier, keepresult, self.tool, self, method, args, kw)
			self.queueregistry[asyncid] = event
			self.queue.append(event)
			self.queue.sort()
			self.queuesync.notify()
			return asyncid
		finally: self.queuesync.release()

	# This method checks wether an event is still in the queue
	def queueWaiting(self, asyncid):
		return self.queueregistry.has_key(asyncid)

