"""

Tool Server Framework - execute a function call in the background

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

import hashlib
import sys
import time
import threading
import traceback

from Toolserver.Config import config
from Toolserver.Context import context
from Toolserver.Utils import logError

_AsyncLock = threading.RLock()
_AsyncRegistry = {}

def createAsyncId(object):
	sig = hashlib.sha1()
	sig.update(time.ctime())
	sig.update(str(threading.currentThread()))
	sig.update(repr(object))
	try:
		_AsyncLock.acquire()
		while _AsyncRegistry.has_key(sig.hexdigest()):
			sig.update(str(time.time()))
		asyncid = sig.hexdigest()
		_AsyncRegistry[asyncid] = object
		return asyncid
	finally: _AsyncLock.release()

def destroyAsyncId(asyncid):
	try:
		_AsyncLock.acquire()
		del _AsyncRegistry[asyncid]
	finally: _AsyncLock.release()

def checkAsyncIdRunning(asyncid):
	return _AsyncRegistry.has_key(asyncid)

def noteAsyncResult(tool, asyncid, res):
	tool.asyncResults[asyncid] = res

def async_call(trigger, tool, data, fun):
	try:
		try:
			(args, kw, asyncid, keepresult) = data
			try:
				context._begin()
				context.asyncid = asyncid
				try:
					tool._begin()
					res = fun(*args, **kw)
					if keepresult: tool.asyncResults[asyncid] = res
				except Exception, e:
					if keepresult: tool.asyncExceptions[asyncid] = e
					tool._abort()
				else:
					tool._commit()
			finally:
				context._end()
		finally: destroyAsyncId(asyncid)

	except:

		(e, d, tb) = sys.exc_info()
		msg = 'ASYNC call exception %s: %s' % (e, d)
		for row in traceback.extract_tb(tb):
			(file, line, function, source) = row
			msg += '<br>%s[%s] in %s' % (file, line, function)
		if type(msg) == type(u''):
			msg = msg.encode(config.documentEncoding)
		logError(msg)

		raise

	if hasattr(fun, 'im_func'):
		return (tool.name, fun.im_func.func_name)
	if hasattr(fun, 'func_name'):
		return (tool.name, fun.func_name)
	else:
		return (tool.name, '?') 

