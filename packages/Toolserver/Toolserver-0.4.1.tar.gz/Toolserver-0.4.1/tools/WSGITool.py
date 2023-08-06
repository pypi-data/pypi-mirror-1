"""

Toolserver Framework for Python - WSGI gateway for toofpy

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

import os
import sys

from socket import gethostbyaddr

from Toolserver.Tool import StandardTool, registerTool, shortversion
from Toolserver.Utils import NotFoundError, EmptyResult, DirectResponseRequest, AlreadyDone, document, logInfo, StringIO
from Toolserver.Config import config
from Toolserver.Context import context
from Toolserver.DefaultConfig import constructPath
from Toolserver.ReactorChain import addChainHead

try:
	from wsgiref.handlers import BaseHandler
	haswsgi = 1
except ImportError:
	haswsgi = 0
	class BaseHandler: pass

try:
	True
	False
except  NameError:
	True = not None
	False = not True

def generate(liste):
	for el in liste:
		yield el

class WSGIGateway(BaseHandler):
	"""
	This class is the actual WSGI Gateway. It translates from the
	tool method call interface (passing in request and POST data) to
	the WSGI interface. It's initialization is run only on app loading
	time, so you can place initialization code there.
	"""

	wsgi_multithread = True
	wsgi_multiprocess = False
	wsgi_run_once = False
	origin_server = False

	def __init__(self, name, callable):
		self._name = name
		self._callable = callable
		for k in self.os_environ.keys():
			if k not in ('PWD', 'PATH', 'USER', 'HOME'):
				del self.os_environ[k]

	def process_medusa_request(self, request, data):
		self._first = None
		try:
			context._begin()
			context.stdin = StringIO(data)
			logInfo("calling WSGI module %s", self._name)
			self.run(self._callable)
			raise AlreadyDone
		finally: context._end()
	
	def get_stdin(self):
		return context.stdin
	
	def get_stderr(self):
		return sys.stderr

	def write(self, data):
		if self._first is None:
			self._first = StringIO()
		self._first.write(data)
	
	def finish_response(self):
		self.iterator = iter(self.result)
		if self._first is None:
			try:
				self._first = self.iterator.next()
			except StopIteration:
				self._first = None
		else:
			self._first = self._first.getvalue()
		request = DirectResponseRequest(context.request)
		request.set_reply_code(self.status)
		request.set_header(str(self.headers))
		context.trigger.pull_trigger(
			lambda request=request, gateway=self: (
				request.push(self),
				request.done(),
				gateway.close()
			)
		)

	def handle_error(self):
		"""
		We don't handle errors in the WSGI framework but just
		forward them to the REST handler to take care.
		"""
		(e, d, tb) = sys.exc_info()
		raise d
	
	def more(self):
		if self._first is not None:
			res = self._first
			self._first = None
			return res
		try:
			res = self.iterator.next()
			if res: return res
			else: raise EmptyResult
		except StopIteration:
			return ''

	def add_cgi_vars(self):
		logInfo("setting up environment for WSGI app %s", self._name)
		self.environ['toofpy.documentencoding'] = config.documentEncoding
		self.environ['SERVER_SOFTWARE'] = shortversion
		self.environ['REQUEST_URI'] = context.request.uri
		self.environ['REQUEST_METHOD'] = context.request.command
		(path, params, query, fragment) = context.request.split_uri()
		self.environ['toofpy.fragment'] = fragment
		self.environ['toofpy.params'] = params
		uri = context.tool.uri+'/'+context.method
		if path.startswith(uri) and path != uri:
			self.environ['SCRIPT_NAME'] = path[:len(uri)]
			self.environ['PATH_INFO'] = path[len(uri):]
			p = os.path.join(config.ROOTDIR, path[len(uri)+1:])
			p = os.path.realpath(p)
			if p.startswith(config.ROOTDIR):
				self.environ['PATH_TRANSLATED'] = p
			else:
				raise NotFoundError(path[len(uri):])
		else:
			self.environ['SCRIPT_NAME'] = path
		self.environ['QUERY_STRING'] = query
		hdr = context.request.get_header('Content-Type')
		if hdr is not None: self.environ['CONTENT_TYPE'] = hdr
		hdr = context.request.get_header('Content-Length')
		if hdr is not None: self.environ['CONTENT_LENGTH'] = hdr
		self.environ['SERVER_NAME'] = config.serverhostname
		self.environ['SERVER_ADDR'] = config.serverip
		self.environ['SERVER_PORT'] = config.serverport
		self.environ['SERVER_PROTOCOL'] = 'HTTP/'+context.request.version
		self.environ['DOCUMENT_ROOT'] = config.ROOTDIR
		self.environ['REMOTE_ADDR'] = context.request.channel.addr[0]
		self.environ['REMOTE_HOST'] = gethostbyaddr(context.request.channel.addr[0])[0]
		if context.client:
			self.environ['REMOTE_USER'] = context.client
			self.environ['AUTH_TYPE'] = context.authtype
		for line in context.request.header:
			(var, value) = line.split(': ', 1)
			hvar = var.strip().replace('-','_').upper()
			self.environ['HTTP_'+hvar] = value.strip()

class WSGIMainTool(StandardTool):

	"""
	This tool manages the list of WSGI applications that are currently
	installed into the framework. It provides the WSGI gateway code to
	those applications. Applications should have a small stub module
	in $HOME/.Toolserver/wsgi/ where you do the registration of your
	application to the WSGITool by calling

	registerWSGI('name', callable_app)

	that is you give your application a name and give the callable that
	will be called with the WSGI environment to process the request
	(registerWSGI is patched into the global namespace temporarily while
	loading all the WSGI applications, so you don't need to import any
	modules).

	You can have additional WSGI mount points - just subclass WSGIMainTool
	and overload the _wsgi_path attribute and register that class
	somewhere else. A sample tool might look like this:

	>>> from Toolserver.Tool import registerTool
	>>> from WSGITool import WSGIMainTool
	>>> 
	>>> class MyWSGIMainTool(WSGIMainTool):
	>>> 
	>>>       _wsgi_path = 'mywsgi'
	>>> 
	>>> registerTool(MyWSGIMainTool, 'LOCAL.WSGI')
	>>>

	WSGI applications are just imported, but their entry in sys.modules
	is deleted right after the import. This is to allow to load multiple
	application files with the same name from different directories.
	This does prevent imports across WSGI apps, though - but that should
	be done on libraries and not the actual application wrappers anyway.
	"""

	_content_type = 'text/html'
	_wsgi_path = 'wsgi'
	_deflate = 0

	def _defaults(self):
		self.wsgipath = constructPath(config.HOMEDIR, self._wsgi_path, mode=0700)

	def _initopts(self, **kw):
		sys.path.insert(0, self.wsgipath)
		oldRegisterWSGI = __builtins__.get('registerWSGI', None)
		__builtins__['registerWSGI'] = self._register
		self.apps = {}
		for app in os.listdir(self.wsgipath):
			(base, ext) = os.path.splitext(app)
			if ext == '.py':
				logInfo("Installing WSGI app %s", base)
				eval(compile("import %s" % base, os.path.join(self.wsgipath, app), 'exec'))
		del sys.path[0]
		if oldRegisterWSGI is None: del __builtins__['registerWSGI']
		else: __builtins__['registerWSGI'] = oldRegisterWSGI
	
	def _rewrite(self, request):
		uri = request.uri[1:]
		for pat in self._urlpatterns:
			if pat.regex.search(uri):
				request.uri = '/WSGI/SANTANA/' + uri
				request._changed = 1
				logInfo("found match for %s in SANTANA, rewritten to %s", request.uri, request.uri)
				return request
		return request

	def _validate_RPC(self, *args, **kw):
		raise ForbiddenError('No RPC')

	def _register(self, name, callable):
		self.apps[name] = (name, callable)
	
	def __getattr__(self, name):
		if self.apps.has_key(name):
			return WSGIGateway(*self.apps[name]).process_medusa_request
		else: raise AttributeError(name)

if haswsgi:
	registerTool(WSGIMainTool, 'WSGI')

