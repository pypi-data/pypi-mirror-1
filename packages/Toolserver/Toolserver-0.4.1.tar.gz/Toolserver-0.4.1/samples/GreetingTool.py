"""

Toolserver Framework for Python - Simple Hello World Tool

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

import zlib
import time

from Toolserver.Config import config
from Toolserver.Context import context
from Toolserver.Tool import registerTool, StandardTool
from Toolserver.Utils import parseQueryFromRequest, parseQueryFromString, ForbiddenError, AuthError, quote
from Toolserver.TagRenderer import xml

from Toolserver.RewriteHandler import patchHostAndPath
from Toolserver.ReactorChain import addChainHead

def patchRequest(request):
	(path, params, query, fragment) = request.split_uri()
	print 'checking ', path
	if path == '/greeting/greet':
		patchHostAndPath(request, request.host, '/greeting/greeting')
	return request

addChainHead('system.request.rewrite', patchRequest)

# fetch different renderer for different documents
response = xml('response')

class GreetingTool(StandardTool):

	"""
	This tool shows several aspects of the Toolserver Framework for
	Python in action. It has it's own API documentation and generates
	automatically a WSDL document with all methods exposed.
	"""

	# These are type declarations for WSDL generation. If you refer to
	# types you define yourself, use the typens: namespace. If you refer
	# to system defined types, use the xsd: namespace!
	_types = StandardTool._types + (
		('stringArray', ['xsd:string']),
		('stringStruct', {'anton':'xsd:string', 'berta':'xsd:string'})
	)

	def _initopts(self):
		self.instanceVar = 0

	def _defaults(self):
		self.config.configvar = 'anton'

	def _invariant(self):
		"""
		Invariant for the tool. This is checked after and before every
		API call to ensure that everything works as specified. It is
		only called when the toolserver is started with the -c switch.
		"""
		assert type(self.instanceVar) == type(1), "instanceVar is an integer"
	
	def _shutdown(self):
		"""
		This method is called under transaction control when the server
		is shut down. If you need to run outside transaction control,
		define _terminate instead.
		"""
		pass

	# this method check access to static content below the tools
	# namespace. parts is the list of name elements that lead to the
	# static content, relative to the tools base namespace.
	def _validate_HTTP(self, request, parts):
		if parts[0] == 'blubb':
			raise ForbiddenError('go away')
		elif parts[0] == 'blubber':
			raise AuthError('blubber')
		elif parts[0] == 'blabber':
			return 'blabber'
		else:
			return ''

	def greeting(self, name, delay):
		"""
		This method can be called with all three kinds of call:
		XML-RPC, SOAP and REST. To make REST calling possible, there are
		several wrappers defined that parse parameters out of the
		request object and generate results in a format for this
		REST call.
		"""
		if config.verbose:
			print "calling greeting(%s, %s)" % (repr(name), repr(delay))
		time.sleep(delay)
		self.instanceVar = delay
		if name.startswith('uncompressed '):
			context.deflate = 0
		return 'Hello %s!' % name

	greeting_signature = ('xsd:string', 'xsd:string', 'xsd:int')

	greeting_content_type = 'text/xml'

	# this method is guarded with pre and post conditions to ensure
	# that the programming contract is fullfilled.
	# If you run your toolserver with -c, these will be checked

	def greeting_pre_condition(self, name, delay):
		assert type(name) in (type(''), type(u'')), "Type of name must be string"
		assert type(delay) == type(1), "Type of delay must be integer"

	def greeting_post_condition(self, result):
		assert type(result) in (type(''), type(u'')), "Type of result must be string"

	def greeting_parser_GET(self, request, data):
		"""
		The parameters are passed in as named query parameters. The name
		is identical to the API parameter name.
		"""
		form = parseQueryFromRequest(request)
		name = form.get('name', [''])[0]
		delay = int(form.get('delay', [0])[0])
		return ([name, delay], {})
	
	greeting_parser_HEAD = greeting_parser_GET

	def greeting_parser_POST(self, request, data):
		"""
		The parameters are passed in as named form parameters whose
		names are identical with the API parameter names.
		"""
		form = parseQueryFromString(data)
		name = form.get('name', [''])[0]
		delay = int(form.get('delay', [0])[0])
		return ([name, delay], {})

	def greeting_generator(self, request, result):
		"""
		Turn the resulting message into a XML document.
		"""
		msg = response.response(response.message(result))
		return msg

	def _error(self, request, error, detail, traceback):
		"""
		Exceptions are formatted as a special XML document that
		includes the message, the detail and the traceback of the
		exception.
		"""
		lines = []
		for row in traceback:
			lines.append(response.line(
				response.file(row[0]),
				response.line(row[1]),
				response.function(row[2]),
				response.source(quote(row[3]))
			))
		msg = response.response(
			response.error(
				response.message(error),
				response.detail(detail)
			),
			response.traceback(lines)
		)
		return msg
	
	def restricted(self, request, data):
		"""
		This method is restricted by a user and a password. You
		need to use user 'hugo' with password 'blubb' to get
		the result. Only GET is allowed, all other access - even
		RPC type access - is forbidden.
		"""
		msg = response.response(response.message('successfull'))
		return msg
	
	def restricted_validate_GET(self, request):
		if context.client != 'hugo':
			return 'restricted'
		return ''
	
	def restricted_validate(self, request):
		raise ForbiddenError('restricted')
	
	def restricted_validate_RPC(self, *args, **kw):
		raise ForbiddenError('restricted')

	compressed_deflate = 0
	def compressed_GET(self, request, data):
		"""
		This method itself deflates it's result, so the server
		shouldn't be allowed to do compression. Otherwise the content
		would be encoded two times.
		"""
		request['Content-encoding'] = 'deflate'
		return zlib.compress('Hello World, this is a compressed string!'*50)
	
	def echoStrings(self, strings):
		"""
		This method returns the strings concatenated. This
		can be used to test complex SOAP signatures.
		"""
		return ' '.join(strings)
	
	echoStrings_signature = ('xsd:string', 'typens:stringArray')
	
	def echoStruct(self, struct):
		"""
		This method returns a string that is concatenated
		from the keys and values of a dictionary. This is used
		to demonstrate complex SOAP signatures, too.
		"""
		return ', '.join(map(lambda k: '%s=%s' % (k, struct[k]), struct.keys()))
	
	echoStruct_signature = ('xsd:string', 'typens:stringStruct')

	def start(self, string, seconds):
		"""
		This method starts a background processing and returns
		the identifier to check the status of this processing.
		"""
		if config.verbose:
			print 'starting background thread to output %s' % string
		asyncid = self._async(self._background, string, seconds)
		if config.verbose:
			print '... using async id %s' % asyncid
		return asyncid
	
	start_signature = ('xsd:string', 'xsd:string', 'xsd:int')

	def running(self, asyncid):
		"""
		Checks wether a process is still running.
		"""
		return self._asyncActive(asyncid)
	
	running_signature = ('xsd:int', 'xsd:string')

	def result(self, asyncid):
		"""
		Returns the result (or the exceptioin) of a background
		process.
		"""
		return self._asyncResult(asyncid)
	
	result_signature = ('xsd:string', 'xsd:string')

	def _background(self, string, seconds):
		if config.verbose:
			print "calling _background(%s, %s)" % (repr(string), repr(seconds))
		time.sleep(seconds)
		return string
	
	def blocking(self, seconds):
		"""
		This call will do a blocking sleep so only one of this
		call can process at the same time. This uses the tool
		level locking.
		"""
		try:
			self._acquire()
			time.sleep(seconds)
		finally: self._release()
	
	blocking_signature = ('xsd:string', 'xsd:int')

	def blockingRead(self):
		"""
		This call is just a blocking read method - it returns
		directly without delay, but tries to lock the tool.
		"""
		try:
			self._acquire()
			return 'success'
		finally: self._release()
	
	blockingRead_signature = ('xsd:string',)
	
	def startat(self, timespec, string, seconds):
		"""
		This method starts a background process at a defined
		time. It uses the timed execution feature.
		"""
		if config.verbose:
			print 'starting timer in %d seconds' % int(timespec - time.time())
		asyncid = self._timed(timespec, self._background, string, seconds)
		if config.verbose:
			print '... using async id %s' % asyncid
		return asyncid
	
	startat_signature = ('xsd:int', 'xsd:string', 'xsd:int')
	
	def waiting(self, asyncid):
		"""
		Checks wether a background process is still waiting for
		execution.
		"""
		return self._timedWaiting(asyncid)
	
	waiting_signature = ('xsd:int', 'xsd:string')

registerTool(GreetingTool, 'greeting')

