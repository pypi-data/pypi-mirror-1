"""

Tool Server Framework - execute a REST call

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

import re
import sys
import hashlib
import traceback

from Toolserver.Config import config, hasCrypto
from Toolserver.Context import context
from Toolserver.Utils import logWarning, logError, ForbiddenError, AuthError, NotChangedError, DirectResponse, AlreadyDone, DirectResponseRequest
from Toolserver.Utils import NotFoundError, RedirectError, findWrapper, callWrapper, Apply, shortenModuleFile, checkForEncoding, tryDeflateEncoding
from Toolserver.Tool import hasTool, getTool
from Toolserver.Authentication import checkAuthentication, generateAuthentication, generateRSAAuthentication

from medusa import http_server

IF_NONE_MATCH = re.compile(r'^If-None-Match: (.*)$', re.IGNORECASE)

HEADER_BODY = re.compile(r'\r?\n\r?\n', re.DOTALL)

def debug_input_headers(request):
	print '*' * 20, 'INPUT HEADERS', '*' * 20
	for line in request.header:
		print line
	print

def debug_output_headers(request):
	print '*' * 20, 'OUTPUT HEADERS', '*' * 20
	for key in request.reply_headers.keys():
		print '%s: %s' % (key, request.reply_headers[key])
	print

def continue_request (trigger, handler, data, request):
	if config.debugrpc:
		debug_input_headers(request)

	tool = request.rest_tool
	base = tool.name
	method = request.rest_method

	acc_deflate = checkForEncoding(request, 'deflate')

	etag = None
	match = http_server.get_header_match(IF_NONE_MATCH, request.header)
	if match:
		etag = match.group(1)

	response = ''

	try:
		if method.find('_') >= 0:
			raise ForbiddenError(method)

		try:

			meth = None
			if hasattr(tool, '%s_%s' % (method, request.command)):
				meth = getattr(tool, '%s_%s' % (method, request.command))
			elif hasattr(tool, method):
				meth = getattr(tool, method)
			if meth:
				try:
					context._begin()
					try:
						(authmethod, client, groups) = checkAuthentication(request, data, tool._realm, tool._checkrsa)
						context.client = client
						context.groups = groups
						context.authtype = authmethod
						context.request = request
						context.trigger = trigger
						context.tool = tool
						context.method = method
						context.deflate = acc_deflate
						tool._begin()
						realm = callWrapper(tool, method, 'validate', request.command, request)
						if realm: raise AuthError(realm)

						request['Content-type'] = 'text/html'
						contenttype = findWrapper(tool, method, 'content_type', request.command)
						if contenttype: request['Content-type'] = contenttype
						dodeflate = findWrapper(tool, method, 'deflate', request.command)
						if acc_deflate and dodeflate is not None:
							context.deflate = dodeflate

						parser = findWrapper(tool, method, 'parser', request.command)
						if parser: (args, kw) = parser(request, data)
						else: (args, kw) = ((request, data), {})

						fr = Apply(tool, method, meth, args, kw)

						generator = findWrapper(tool, method, 'generator', request.command)
						if generator: response = generator(request, fr)
						else:
							if type(fr) == type(''): response = fr
							elif type(fr) == type(u''): response = fr.encode(config.documentEncoding)
							else: raise TypeError(fr)

						acc_deflate = context.deflate

						sig = hashlib.sha1()
						sig.update(response)
						sig = '"%s"' % sig.hexdigest()
						request['ETag'] = sig
						if etag and sig == etag:
							raise NotChangedError()

					except AlreadyDone:
						tool._commit()
						return (base, method)
					except DirectResponse, e:
						(header, body) = HEADER_BODY.split(e.value, 1)
						request=DirectResponseRequest(request, header)
						tool._commit()
						trigger.pull_trigger(
							lambda request=request, response=body: (
								request.push (response),
								request.done()
							)
						)
						return (base, method)
					except NotChangedError:
						tool._commit()
						trigger.pull_trigger(
							lambda request=request: request.error(304)
						)
						return (base, method)
					except ForbiddenError:
						tool._abort()
						trigger.pull_trigger(
							lambda request=request: request.error(403)
						)
						return (base, method)
					except NotFoundError:
						tool._abort()
						trigger.pull_trigger(
							lambda request=request: request.error(404)
						)
						return (base, method)
					except NotImplementedError:
						tool._abort()
						trigger.pull_trigger(
							lambda request=request: request.error(501)
						)
						return (base, method)
					except AuthError, e:
						tool._abort()
						generateAuthentication(request, e.realm)
						trigger.pull_trigger(
							lambda request=request: request.error(401)
						)
						return (base, method)
					except RedirectError, e:
						tool._commit()
						logWarning('Redirect to %s', e.url)
						request['Location'] = e.url
						trigger.pull_trigger(
							lambda request=request: request.error(302)
						)
						return (base, method)
					except:
						tool._abort()
						raise
					else:
						tool._commit()
				finally:
					context._end()

			else:
				raise NotFoundError(method)
		except:
			# report exception back to server
			(e, d, tb) = sys.exc_info()
			request.reply_code = 500
			request['X-REST-Errorobject'] = str(e)
			request['X-REST-Errordetail'] = str(d)
			if hasattr(tool, '%s_error_%s' % (method, request.command)):
				response = getattr(tool, '%s_error_%s' % (method, request.command))(request, e, d, traceback.extract_tb(tb))
			elif hasattr(tool, '%s_error' % method):
				response = getattr(tool, '%s_error' % method)(request, e, d, traceback.extract_tb(tb))
			elif hasattr(tool, '_error'):
				response = getattr(tool, '_error')(request, e, d, traceback.extract_tb(tb))
			msg = 'REST call exception %s: %s' % (e, d)
			for row in traceback.extract_tb(tb):
				(file, line, function, source) = row
				file = shortenModuleFile(file)
				msg += '<br>%s[%s] in %s' % (file, line, function)
			if type(msg) == type(u''):
				msg = msg.encode(config.documentEncoding)
			logError(msg.replace('%','%%'))
			handler._errorcounter += 1
		else:
			handler._callcounter += 1


	except NotFoundError:
			
		trigger.pull_trigger(lambda request=request: request.error(404))
		handler._errorcounter += 1
		return (base, method)

	except ForbiddenError:
			
		trigger.pull_trigger(lambda request=request: request.error(403))
		handler._errorcounter += 1
		return (base, method)

	except:
		# internal error, report as HTTP server error
		(e, d, tb) = sys.exc_info()
		request.reply_code = 500
		request['X-REST-Errorobject'] = str(e)
		request['X-REST-Errordetails'] = str(d)
		msg = 'REST call exception %s: %s' % (e, d)
		for row in traceback.extract_tb(tb):
			(file, line, function, source) = row
			file = shortenModuleFile(file)
			msg += '<br>%s[%s] in %s' % (file, line, function)
		if type(msg) == type(u''):
			msg = msg.encode(config.documentEncoding)
		logError(msg.replace('%','%%'))
		handler._errorcounter += 1

	# got a valid REST response, trigger delivery
	# but only send out the response if it's not a HEAD
	# request! With HEAD requests just send the header, nothing
	# more!
	if config.debugrpc:
		debug_output_headers(request)
	if request.command != 'HEAD':
		if hasCrypto and config.rsaauthenticate and tool._checkrsa:
			generateRSAAuthentication(request, response)
		if acc_deflate:
			response = tryDeflateEncoding(request, response)
		request['Content-length'] = len(response)
		trigger.pull_trigger(
			lambda request=request, response=response: (
				request.push (response),
				request.done()
			)
		)
	else:
		trigger.pull_trigger(
			lambda request=request: request.done()
		)
	return (base, method)

