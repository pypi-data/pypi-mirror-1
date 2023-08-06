"""
Toolserver Framework for Python - HTTP handler with authentication

Copyright (c) 2002, Georg Bauer <gb@rfc1437.de>, except where the file
explicitly names other copyright holders and licenses.

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

from Toolserver.Tool import getFirstToolForPath
from Toolserver.Utils import AuthError, ForbiddenError
from Toolserver.Authentication import checkAuthentication
from Toolserver.Context import context

from medusa import default_handler

class http_handler(default_handler.default_handler):

	def handle_request (self, request):
		[path, params, query, fragment] = request.split_uri()
		try:
			(tool, parts) = getFirstToolForPath(path)
			if hasattr(tool, '_validate_HTTP'):
				(authmethod, client, groups) = checkAuthentication(request, '', tool._realm, 0)
				try:
					context._begin()
					context.request = request
					context.client = client
					context.groups = groups
					context.authtype = authmethod
					realm = tool._validate_HTTP(request, parts)
					if realm: raise AuthError(realm)
				finally:
					context._end()
		except AuthError, e:
			request['WWW-Authenticate'] = 'Basic realm="%s"' % e.realm
			request.error(401)
			return
		except ForbiddenError:
			request.error(403)
			return
		except KeyError: pass
		except: raise
		return default_handler.default_handler.handle_request(self, request)

