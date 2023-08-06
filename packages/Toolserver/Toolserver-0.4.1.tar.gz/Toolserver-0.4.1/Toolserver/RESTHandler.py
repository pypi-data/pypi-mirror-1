# -*- Mode: Python -*-

# this is a handler for REST style access to functions. It is based
# on the medusa xmlrpc_handler.py and was adapted by Georg Bauer

# See http://www.xml-rpc.com/
#     http://www.pythonware.com/products/xmlrpc/

# Based on "xmlrpcserver.py" by Fredrik Lundh (fredrik@pythonware.com)

from Toolserver.Tool import getToolForPath, getFirstToolForPath
from Toolserver.Worker import dispatcher
from Toolserver.RESTCall import continue_request
from Toolserver.RPCHandler import base_handler, collector
from Toolserver.Utils import logInfo

class rest_handler(base_handler):

	def match (self, request):
		(path, params, query, fragment) = request.split_uri()
		tool = method = None
		try:
			(tool, method) = getToolForPath(path)
			if hasattr(tool, method) or hasattr(tool, method+'_'+request.command):
				request.rest_tool = tool
				request.rest_method = method
				logInfo('found method %s in tool %s', method, tool)
				return 1
		except KeyError:
			pass
		except:
			raise
		try:
			(tool, parts) = getFirstToolForPath(path)
			if not len(parts):
				logInfo('no match for tool %s - no parts', tool)
				return 0
			method = parts[0]
			if not hasattr(tool, parts[0]):
				logInfo('no match for tool %s - method %s not found', tool, method)
				return 0
			if not parts[-1]: parts[-1] = 'index.html'
			if tool._exists('/'.join(parts)):
				logInfo('no match for tool %s - static content at %s', tool, '/'.join(parts))
				return 0
		except KeyError:
			return 0
		except:
			raise
		logInfo('found upstairs method %s in tool %s', method, tool)
		request.rest_tool = tool
		request.rest_method = method
		return 1

	def handle_request (self, request):
		[path, params, query, fragment] = request.split_uri()

		if request.command in ('POST', 'PUT'):
			request.collector = collector(self, request)
		elif request.command in ('GET', 'HEAD', 'DELETE'):
			self.continue_request('', request)
		else:
			request.error(400)

	def continue_request (self, data, request):
		dispatcher.append(self, continue_request, data, request)

