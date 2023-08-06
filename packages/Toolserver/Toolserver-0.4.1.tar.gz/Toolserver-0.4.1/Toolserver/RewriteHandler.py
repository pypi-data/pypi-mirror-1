# -*- Mode: Python -*-

# this is a handler to rewrite request objects based on the
# pycs_rewrite_handler and was adapted for TooFPy by Georg Bauer

import re

from Toolserver.ReactorChain import runChain
from Toolserver.Utils import logInfo

def patchHeader(request, headers):
	"""
	This function patches a header in the request object. This is
	actually quite hacky - we need to know about how the request
	object is built internally. So this might break with newer
	versions of medusa, but it's unlikely. You pass in a sequence of
	(header, value) tuples.
	"""
	for (header, value) in headers:
		request._header_cache[header.lower()] = value
	newheader = []
	for line in request.header:
		found = 0
		for (header, value) in headers:
			if line.lower().startswith(header+': '):
				newheader.append('%s: %s' % (header, value))
				found = 1
		if not(found):
			newheader.append(line)
	request.header = newheader
	request._changed = 1

def patchRequest(request, host=None, path=None, params=None, query=None, fragment=None, headers=[]):
	"""
	This function patches the full request with all parts. This allows
	to rebuild everything important of the header, even doing query
	rewrites and stuff like that. All parameters are filled with
	defaults from the original request if you don't pass them in.
	"""
	(opath, oparams, oquery, ofragment) = request.split_uri()
	changed = 0
	if path is not None and path != opath:
		changed = 1
		opath = path
	if params is not None and params != oparams:
		changed = 1
		oparams = params
	if query is not None and query != oquery:
		changed = 1
		oquery = query
	if fragment is not None and fragment != ofragment:
		changed = 1
		ofragment = fragment
	if changed:
		request._changed = 1
		request._split_uri = (opath, oparams, oquery, ofragment)
		request.uri = ''.join(filter(lambda e: e, request._split_uri))
		request.request = '%s %s HTTP/%s' % (
			request.command,
			request.uri,
			request.version
		)
	if request.host != host:
		request.host = host
		headers = copy.copy(headers)
		headers.append(('Host', host))
	if len(headers):
		patchHeader(request, headers)

def patchHostAndPath(request, host, path):
	"""
	This function patches the host and path of a request object. It's
	what you usually use to change something in the request in your
	tools - for example change the URI based on some virtual host
	mapping. This is given as an explicit function because it is a
	very usual patching you will do.
	"""
	patchRequest(request, host=host, path=path)

class rewrite_handler:

	"""
	This handler provides a hook to rewrite URIs in the request
	object. It just set's up the request.host variable for convenience
	of tools hooking into system.request.rewrite and runs the chain. To
	do the actual patching, use one of the defined patch methods. If
	you don't use those methods, the request will not be marked as
	changed and so won't be installed!
	"""

	def match (self, request):

		host = request.get_header('host')
		if host:
			request.host = host
		else:
			request.host = config.serverhostname

		request._changed = 0

		nrequest = runChain('system.request.rewrite', request)
		if nrequest._changed:
			if nrequest.uri != request.uri:
				logInfo('rewritten %s as %s', request.uri, nrequest.uri)

				request.host = nrequest.host
				request.uri = nrequest.uri
				request._split_uri = nrequest._split_uri
				request.request = nrequest.request
			request.header = nrequest.header

		del request._changed

		return 0
 
