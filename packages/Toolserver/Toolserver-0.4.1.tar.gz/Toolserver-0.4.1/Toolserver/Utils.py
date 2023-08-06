"""

Toolserver Framework for Python - Utility functions

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
import re
import hashlib
import base64
import random
import cgi
import inspect
import zlib

from medusa import http_server

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

from Toolserver.Config import config

# regexps for HTTP headers
AUTHORIZATION = re.compile(r'^Authorization: ([^ ]+) (.*)$', re.IGNORECASE)

# this exception is thrown by the medusa producers if they want to tell
# the server that they don't have anything to say currently. They can't return
# an empty string as that is interpreted as EOF by medusa.
class EmptyResult(Exception):

	def __str__(self):
		return '<EmptyResult Exception>'

# this error is thrown to produce direct responses from
# tools. That way no header and status handling of toofpy kicks
# in, but you need to directly provide all relevant headers in your
# result string. This is much like how CGIs work
class DirectResponse(Exception):

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return '<DirectResponse Exception: %s>' % self.value

# This error is thrown when you want to tell the system that you already
# pushed everything out that was there to push.
class AlreadyDone(Exception):
	
	def __str__(self):
		return '<AlreadyDone Exception>'

# this error is thrown if the user tries to do something
# that is forbidden and can't be overridden with authentication
class ForbiddenError(Exception):

	def __init__(self, value):
		self.detail = value

	def __str__(self):
		return '<ForbiddenError Exception: %s>' % self.detail

# This exception can be thrown if something is obsolete
class ObsoleteError(Exception):

	def __init__(self, value):
		self.name = '.'.join(value)

	def __str__(self):
		return '<ObsoleteError: %s>' % self.name

# this error can be thrown to signal that a computation
# doesn't need to take place because nothing changed or
# that stuff needs not to be transferred because it's
# already on the other side.
class NotChangedError(Exception):
	
	def __str__(self):
		return '<NotChangedError Exception>'


# this error is thrown to trigger a 404 response
class NotFoundError(Exception):

	def __init__(self, value):
		self.detail = value

	def __str__(self):
		return '<NotFoundError Exception: %s>' % self.detail

# this error is thrown to trigger a 302 response
class RedirectError(Exception):

	def __init__(self, value):
		self.url = value

	def __str__(self):
		return '<RedirectError Exception: %s>' % self.url

# this error is thrown if you need authentication to
# access some part. It should carry the authentication
# realm as payload.
class AuthError(Exception):
	
	def __init__(self, realm):
		self.realm = realm

	def __str__(self):
		return '<AuthError Exception: %s>' % self.realm

# these messages are only logged if verbose is true
def logWarning(fmt, *args):
	msg = fmt % args
	if config.verbose:
		sys.stderr.write(msg)
		sys.stderr.write('\n')

# these messages are only logged if verbose is above 1
def logInfo(fmt, *args):
	msg = fmt % args
	if config.verbose > 1:
		sys.stderr.write(msg)
		sys.stderr.write('\n')

# these messages are logged allways
def logError(fmt, *args):
	msg = fmt % args
	sys.stderr.write(msg)
	sys.stderr.write('\n')

# quote a string so it can be used in XML or HTML
def quote(s):
	s = s.replace('&', '&amp;')
	s = s.replace('<', '&lt;')
	s = s.replace('>', '&gt;')
	s = s.replace('"', '&quot;')
	return s

# produce a simple HTML document out of a fragment
def document(title, body):
	response = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
	response += '<html>'
	response += '<head><title>%s</title>' % title
	response += '<style type="text/css" media="screen">\n'
	response += '<!--\n'
	response += 'body { background-color: white; font-family: verdana, sans-serif; }\n'
	response += 'h1 { background-color: lightgreen; text-align: left; border: solid; border-color: green; padding: 0.25em; }\n'
	response += 'h2 { background-color: #f0fff0; text-align: left; border: dashed; border-color: green; border-width: 1px; padding: 0.25em; }\n'
	response += 'dt { font-weight: bold; padding-top: 1em; }\n'
	response += '-->\n'
	response += '</style></head>'

	response += '<body>%s</body>' % body
	response += '</html>'

	return response

# simple format a documentation string
def format(docstr):
	paras = str(docstr).split('\n\n')
	liste = []
	for para in paras:
		liste.append('<p>')
		incode = 0
		for line in para.split('\n'):
			if line.strip().startswith('>>>'):
				if not incode:
					incode = 1
					liste.append('<pre>')
				liste.append(quote(line.strip()))
				liste.append('\n')
			else:
				if incode:
					incode = 0
					liste.append('</pre>')
				liste.append(quote(line))
		if incode:
			liste.append('</pre>')
	return ''.join(liste)

# simple source formatting function
def formatSource(obj):
	src = inspect.getsource(obj)
	doc = obj.__doc__
	dl = []
	if doc:
		doc = doc.replace('\r\n', '\n')
		doc = doc.replace('\r', '\n')
		dl = map(lambda l: l.strip(), doc.split('\n'))
	src = src.replace('\r\n', '\n')
	src = src.replace('\r', '\n')
	l = []
	for line in src.split('\n'):
		i = indent = 0
		while i < len(line) and line[i] in (' ', '\t'):
			if line[i] == ' ': indent += 1
			elif line[i] == '\t': indent = (int(indent/8)+1)*8
			i += 1
		l.append((indent, quote(line.strip())))
	ls = []
	base = l[1][0]
	where = 0
	if dl == []: where = 2
	for (indent, src) in l[1:]:
		if where == 0:
			if src in dl: where = 1
		elif where == 1:
			if src not in dl:
				where = 2
				if src != '"""':
					ls.append('&nbsp;'*(indent-base)+src)
		elif where == 2: ls.append('&nbsp;'*(indent-base)+src)
	if doc: return '<p>'+doc+'<p>'+'<br>'.join(ls)
	else: return '<br>'.join(ls)

# check wether some encoding is in the headers
def checkForEncoding(request, encoding):
	input = request.get_header('accept-encoding')
	if input == '*':
		return 1
	elif input:
		for part in input.split(','):
			if part.find(';') >= 0:
				if part.strip().startswith(encoding+';'):
					return 1
			elif part.strip() == encoding:
				return 1
	else: return 0

# try to use deflate encoding if it reduces response size
def tryDeflateEncoding(request, response):
	s = zlib.compress(response)
	if len(s) < len(response):
		logInfo('saving %d bytes by compression', len(response)-len(s))
		request['Content-encoding'] = 'deflate'
		return s
	else: return response

# parse a query string that's still in it's request object
def parseQueryFromRequest(request):
	(path, params, query, fragment) = request.split_uri()
	form = {}
	if query:
		if query[0] == '?': query = query[1:]
		form = cgi.parse_qs(query)
	return form

# parse an explicit query string
def parseQueryFromString(query):
	form = {}
	if query:
		if query[0] == '?': query = query[1:]
		form = cgi.parse_qs(query)
	return form

# This function shortens a path name by any prefix form the sys.path
def shortenModuleFile(file):
	prefix = ''
	for p in sys.path:
		if file.startswith(p) and len(p) > len(prefix):
			prefix = p
	file = file[len(prefix):]
	if file.startswith('/'):
		file = file[1:]
	return file

# This is a cache for wrapper method lookups. This speeds
# up things after the first lookup!
_Wrappers = {}

# This function returns an attribute of a tool, specified
# by methodname, qualifier and command. It drops consecutively
# the command and the methodname if the attribute is not found.
def findWrapper(tool, name, qualifier, command):
	k = (tool.name, name, qualifier, command)
	if _Wrappers.has_key(k):
		return _Wrappers[k]
	wrapper = None
	meth1 = '_' + qualifier
	meth2 = name + meth1
	meth3 = meth2 + '_' + command
	if hasattr(tool, meth3):
		wrapper = getattr(tool, meth3)
	elif hasattr(tool, meth2):
		wrapper = getattr(tool, meth2)
	elif hasattr(tool, meth1):
		wrapper = getattr(tool, meth1)
	elif wrapper is not None:
		_Wrappers[k] = wrapper
	return wrapper

# This function calls a method of a tool that
# is specified by a base method name, a qualifier
# and a HTTP command. It starts with full qualification
# and then drops the command and drops the method name.
def callWrapper(tool, method, qualifier, command, *args, **kw):
	wrap = findWrapper(tool, method, qualifier, command)
	if wrap: return wrap(*args, **kw)
	return None

# This function calls the correct validation wrapper
# for RPC calls. It caches the found wrapper, too.
def validateWrapper(protocol, tool, method, args, kw=None):
	k = (protocol, tool.name, method)
	if _Wrappers.has_key(k):
		wrapper = _Wrappers[k]
	else:
		wrapper = None
		if hasattr(tool, '%s_validate_RPC_%s' % (method, protocol)):
			wrapper = getattr(tool, '%s_validate_RPC_%s' % (method, protocol))
		elif hasattr(tool, '%s_validate_RPC' % method):
			wrapper = getattr(tool, '%s_validate_RPC' % method)
		elif hasattr(tool, '_validate_RPC_%s' % protocol):
			wrapper = getattr(tool, '_validate_RPC_%s' % protocol)
		elif hasattr(tool, '_validate_RPC'):
			wrapper = getattr(tool, '_validate_RPC')
		_Wrappers[k] = wrapper
	if wrapper:
		if kw is None: return apply(wrapper, args)
		else: return apply(wrapper, args, kw)
	else: return None

# This function calls a method with contract insurance
def contractApply(tool, method, meth, args, kw=None):
	if config.verbose: print ">>> checking contracts for %s.%s" % (tool.name, method)
	pre = post = invar = None
	if hasattr(tool, '_invariant'):
		invar = getattr(tool, '_invariant')
	if meth is None:
		meth = getattr(tool, method)
	prename = method+'_pre_condition'
	if hasattr(tool, prename):
		pre = getattr(tool, prename)
	postname = method+'_post_condition'
	if hasattr(tool, postname):
		post = getattr(tool, postname)
	try:
		if invar: invar()
		if kw is None:
			if pre: apply(pre, args)
			fr = apply(meth, args)
			if post: post(fr)
			return fr
		else:
			if pre: apply(pre, args, kw)
			fr = apply(meth, args, kw)
			if post: post(fr)
			return fr
	finally:
		if invar: invar()

# This is an apply that doesn't use contracts
def noContractApply(tool, method, meth, args, kw=None):
	if meth is None:
		meth = getattr(tool, method)
	if kw is None:
		return apply(meth, args)
	else:
		return apply(meth, args, kw)

# This is the Apply method based on the
# contract flag. This only takes into account
# the globally set flag from your toolserver
# configuration. The dynamic switching is
# done in tsctl
Apply = noContractApply
if config.contract: Apply = contractApply

# This function creates a shared secret that can
# be used for transient passwords or security tokens
def genSecret(*parts):
	secret = hashlib.sha1()
	for part in parts:
		secret.update(str(part))
	return secret.hexdigest().strip()

# these functions are for security tokens that
# are only alloweable for a limited time and
# are based on a private secret
def createToken(maxage, *parts):
	now = time.time()
	then = now+maxage
	return (now, then, genSecret(now, then, *parts))

def checkToken(token, *parts):
	now = time.time()
	(inow, ithen, isig) = token
	if ithen < now:
		return 0
	if isig != genSecret(inow, ithen, *parts):
		return 0
	return 1

# this class fakes a medusa request and overrides only some of the methods.
# It's needed to introduce new functionality or behaviour after the fact -
# after the actual medusa request was created. It does this by copying
# all data over from the original request.
class FakeMedusaRequest(http_server.http_request):

	def __init__(self, request):
		self.__request = request
		for (k,v) in request.__dict__.items():
			if not hasattr(self, k):
				setattr(self, k, v)

HEADERDELIM = re.compile(r'\r?\n')
HEADERCONTINUE = re.compile(r'\r?\n\s+')
HEADER = re.compile(r'^(\S+):\s+(.*)$')

# this class is a faked medusa request that is used for direct response
# style calls. This one allows changing of status messages by the application.
# Additionally this one parses headers from a special header block and builds
# the reply_headers hash accordingly. This is to prevent problems with
# differently written header names and to allow to set all headers in
# the code.
class DirectResponseRequest(FakeMedusaRequest):

	def __init__(self, request, headertext=None):
		FakeMedusaRequest.__init__(self, request)
		self.reply_header = {}
		self.reply_header_source = []
		if headertext: self.set_header(headertext)

	def __setitem__(self, name, value):
		if self.has_key(name):
			idx = self.reply_header[name.lower()]
			self.reply_header_source[idx][1] = value
		else:
			idx = len(self.reply_header_source)
			self.reply_header_source.append([name, value])
			self.reply_header[name.lower()] = idx
	
	def __getitem__(self, name):
		idx = self.reply_header[name.lower()]
		return self.reply_header_source[idx][1]
	
	def has_key(self, name):
		return self.reply_header.has_key(name.lower())

	def build_reply_header(self):
		return '\r\n'.join(
			[self.response(self.reply_code_full)]+map(
				lambda e: '%s: %s' % tuple(e),
					self.reply_header_source
				)
			)+'\r\n\r\n'

	def response(self, code=200):
		self.set_reply_code(code)
		return 'HTTP/%s %s' % (self.version, self.reply_code_full)
	
	def set_reply_code(self, code):
		if type(code) == type(1):
			message = self.responses[code]
			self.reply_code = code
			self.reply_code_full = '%d %s' % (code, message)
		else:
			self.reply_code = int(code.split()[0])
			self.reply_code_full = code

	def set_header(self, header):
		self.reply_header = {}
		self.reply_header_source = []
		header = HEADERCONTINUE.sub(' ', header)
		for l in HEADERDELIM.split(header):
			m = HEADER.match(l)
			if m and m.group(1).lower() == 'status':
				self.set_reply_code(m.group(2))
			elif m:
				self[m.group(1)] = m.group(2)
	

