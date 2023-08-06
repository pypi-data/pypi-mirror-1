# -*- Mode: Python -*-

# See http://www.xml-rpc.com/
#     http://www.pythonware.com/products/xmlrpc/

# Based on "xmlrpcserver.py" by Fredrik Lundh (fredrik@pythonware.com)

VERSION = "$Id: RPCHandler.py 308 2004-11-15 21:55:35Z gb $"

import sys
import zlib
import string
import traceback

try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO

from base64 import encodestring, decodestring

from medusa import producers
from medusa.status_handler import html_repr

from Toolserver.Config import config, hasCrypto
from Toolserver.Context import context
from Toolserver.Utils import logInfo, logError, ForbiddenError, AuthError, Apply, validateWrapper, shortenModuleFile, checkForEncoding, tryDeflateEncoding
from Toolserver.Tool import hasTool, getTool
from Toolserver.Worker import dispatcher
from Toolserver.Authentication import checkAuthentication, generateAuthentication, generateRSAAuthentication

# handle registration of RPC handlers
registered_handler_classes = []

def registerRPCHandler(klass):
	registered_handler_classes.append(klass)

def getRegisteredRPCHandlers():
	return registered_handler_classes

class base_handler:

	def __init__(self):
		self._callcounter = 0
		self._errorcounter = 0

	def status(self):
		return producers.lines_producer([
			'<li>%s' % html_repr(self),
			'<ul>',
			'<li><b>Total Calls:</b> %d' % (self._callcounter + self._errorcounter),
			'<li><b>Successfull Calls:</b> %d' % self._callcounter,
			'<li><b>Calls with Errors:</b> %d' % self._errorcounter,
			'</li>'
			'</ul>',
		])

class rpc_handler(base_handler):

	_prefix = 'AbstractRPC'
	_name = 'AbstractRPC'
	_mime_type = 'text/xml'

	def __init__(self):
		base_handler.__init__(self)
		self._match_prefix = '/%s' % self._prefix
		self._method_prefix = '/%s/' % self._prefix
		logInfo('installing %s handler on %s',
			self._name, self._match_prefix
		)

	def debug_input(self, data, request):
		print '*' * 20, 'INPUT %s CODE' % self._name, '*' * 20
		print data

	def debug_output(self, result):
		print '*' * 20, 'OUTPUT %s CODE' % self._name, '*' * 20
		print result

	def traceback_message(self, excinfo):
		(e, d, tb) = excinfo
		msg = '%s call exception %s: %s' % (self._name, e, d)
		for row in traceback.extract_tb(tb):
			(file, line, function, source) = row
			file = shortenModuleFile(file)
			msg += '\n  %s[%s] in %s' % (file, line, function)
		if type(msg) == type(u''):
			msg = msg.encode(config.documentEncoding)
		return msg

	def simplify_value(self, value):
		return value

	def parse_request(self, data, request):
		raise NotImplementedError

	def build_exception(self, request, excinfo, reason):
		raise NotImplementedError

	def build_result(self, request, method, result):
		raise NotImplementedError

	def outgoing_header_hook(self, request, data):
		pass

	def match (self, request):
		if request.uri == self._match_prefix or request.uri.startswith(self._match_prefix+'/'): return 1
		else: return 0

	def handle_request (self, request):
		[path, params, query, fragment] = request.split_uri()

		if request.command == 'POST':
			request.collector = collector (self, request)
		else:
			request.error (400)

	def continue_request (self, data, request):
		dispatcher.append(self, self.process_request, data, request)

	def process_request(self, trigger, handler, data, request):
		if config.debugrpc:
			self.debug_input(data, request)

		acc_deflate = checkForEncoding(request, 'deflate')

		base = '<none>'
		method = '<none>'

		try:
			try:

				(authmethod, client, groups) = checkAuthentication(request, data, 'RPC', 1)

				(args, kw, kwnames, method) = self.parse_request(data, request)

				path, params, query, fragmet = request.split_uri()
				if path.startswith(self._method_prefix):
					method = '%s.%s' % (path[len(self._method_prefix):].replace('/','.'), method)

				parts = method.split('.')
				base = parts[:-1]
				method = parts[-1]

				if method.find('_') >= 0:
					raise ForbiddenError(method)

				if hasTool(base):
					tool = getTool(base)
					if hasattr(tool, method):
						try:
							context._begin()
							context.request = request
							context.client = client
							context.groups = groups
							context.authtype = authmethod
							context.method = method
							context.tool = tool
							try:
								tool._begin()
								meth = getattr(tool, method)
								if len(kwnames):
									code = meth.im_func.func_code
									argnames = code.co_varnames[:code.co_argcount]
									orderedargs = []
									for k in kwnames:
										if k not in argnames:
											if config.simplify: orderedargs.append(self.simplify_value(kw[k]))
											else: orderedargs.append(kw[k])
											del kw[k]
										elif config.simplify: kw[k] = self.simplify_value(kw[k])
									if validateWrapper(self._prefix, tool, method, orderedargs, kw):
										raise ForbiddenError('RPC')
									fr = Apply(tool, method, meth, orderedargs, kw)
								else:
									if validateWrapper(self._prefix, tool, method, args):
										raise ForbiddenError('RPC')
									fr = Apply(tool, method, meth, args)
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

			except AuthError, e:
				generateAuthentication(request, e.realm)
			
				trigger.pull_trigger(lambda request=request: request.error(401))
				handler._errorcounter += 1
				return (base, method)

			except ForbiddenError:
			
				trigger.pull_trigger(lambda request=request: request.error(403))
				handler._errorcounter += 1
				return (base, method)

			except AttributeError:
				excinfo = sys.exc_info()
				response = self.build_exception(request, excinfo, 'method.unknown')
				logError('Unknown %s method %s called' % (self._name, method))
				handler._errorcounter += 1

			except:
				# report exception back to server
				excinfo = sys.exc_info()
				response = self.build_exception(request, excinfo, 'method')
				msg = self.traceback_message(excinfo)
				logError(msg.replace('%','%%'))
				handler._errorcounter += 1
			else:
				response = self.build_result(request, method, fr)
				handler._callcounter += 1
		except:
			# internal error, report as HTTP server error
			excinfo = sys.exc_info()
			response = self.build_exception(request, excinfo, 'server')
			msg = self.traceback_message(excinfo)
			logError(msg.replace('%','%%'))
			handler._errorcounter += 1

		# got a valid RPC response, trigger delivery
		request['Content-type'] = self._mime_type
		if config.debugrpc:
			self.debug_output(response)
		if hasCrypto and config.rsaauthenticate:
			generateRSAAuthentication(request, response)
		if acc_deflate:
			response = tryDeflateEncoding(request, response)
		request['Content-length'] = len(response)
		self.outgoing_header_hook(request, response)
		trigger.pull_trigger(
			lambda request=request, response=response: (
				request.push (response),
				request.done()
			)
		)
		return (base, method)

class collector:

	"gathers input for POST and PUT requests"

	def __init__ (self, handler, request):

		self.handler = handler
		self.request = request
		self.data = StringIO()

		# make sure there's a content-length header
		cl = request.get_header ('content-length')

		if not cl:
			request.error (411)
		else:
			cl = string.atoi (cl)
			# using a 'numeric' terminator
			self.request.channel.set_terminator (cl)

	def collect_incoming_data (self, data):
		self.data.write(data)

	def found_terminator (self):
		# set the terminator back to the default
		self.request.channel.set_terminator ('\r\n\r\n')
		self.handler.continue_request (self.data.getvalue(), self.request)

