"""

Tool Server Framework - manages worker threads

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
import threading

from Toolserver.Config import config
from Toolserver.Utils import logInfo, logWarning, logError
from Toolserver.ReactorChain import runChain
from Toolserver.select_trigger import trigger

# This is just a stub class to carry attributes around
class Globals:
	pass

# This class implements a single worker thread
class Worker(threading.Thread):

	def __init__(self, *args, **kw):
		threading.Thread.__init__(self, *args, **kw)
		self._iAmFree = 1
		self._running = 1
		self._last_activity = time.time()
	
# This class implements the workers for SOAP requests
class WorkerManager:

	def __init__(self):
		self.sync = threading.Condition()
		self.queue = []
		self.running = 1
		self.workers = []
		self.trigger = trigger()
		self.manager = None
	
	def append(self, handler, fun, data, request):
		try:
			self.sync.acquire()
			self.queue.append((handler, fun, data, request))
			self.sync.notify()
		finally: self.sync.release()

	def hasWork(self):
		return len(self.queue)

	def shift(self):
		try:
			self.sync.acquire()
			res = self.queue[0]
			del self.queue[0]
			return res
		finally: self.sync.release()

	def start(self):
		self.manager = threading.Thread(target=self.manage_workers, args=[], kwargs={})
		self.manager.start()

	def manage_workers(self):
		logInfo('manager thread started')
		while self.running:
			if self.sync.acquire(blocking=0):
				try: self.start_stop_workers()
				finally: self.sync.release()
			time.sleep(config.freecheckinterval)
		logInfo('manager thread stopped')

	def start_stop_workers(self):
		freelist = []
		workers = []
		for thread in self.workers:
			if thread.isAlive():
				workers.append(thread)
				if thread._iAmFree:
					freelist.append(thread)
		logInfo('loaded workers: %d, running workers: %d, free workers: %d', len(self.workers), len(workers), len(freelist))
		self.workers = workers
		if len(freelist) < config.minfreeworkers:
			logWarning('Only %d threads free, need to start more', len(freelist))
			if len(workers) + config.startfreeworkers <= config.maxworkers:
				for idx in range(0, config.startfreeworkers):
					thread = Worker(target=self.loop, args=[], kwargs={})
					self.workers.append(thread)
					freelist.append(thread)
					thread.start()
			else:
				logError("Can't start more workers, already %d running", len(workers))
		elif len(freelist) > config.maxfreeworkers:
			logWarning('There are %d threads free, need to stop some', len(freelist))
			freelist.sort(lambda a, b: cmp(a._last_activity, b._last_activity))
			for idx in range(0, len(freelist) - config.maxfreeworkers):
				freelist[idx]._running = 0

	def stop(self):
		self.running = 0
		if self.manager and self.manager.isAlive():
			self.manager.join()
		for thread in self.workers:
			if thread.isAlive():
				thread.join()

	def loop(self):
		me = threading.currentThread()
		try:
			self.sync.acquire()
			me.globals = runChain('system.worker.start', Globals())
			logInfo('free worker thread started: %s' % me)
			while self.running and me._running:
				self.sync.wait(5)
				if me._running and self.running and self.hasWork():
					try:
						me._iAmFree = 0
						me._last_activity = time.time()
						(handler, fun, data, request) = self.shift()
						self.sync.release()
						(tool, method) = fun(self.trigger, handler, data, request)
						logWarning('processed %s.%s in %s', tool, method, me)
					finally:
						me._iAmFree = 1
						self.sync.acquire()
		finally:
			me.globals = runChain('system.worker.exit', me.globals)
			self.sync.release()
			logInfo('free worker thread stopped: %s' % me)

dispatcher = WorkerManager()

def start_worker():
	dispatcher.start()

