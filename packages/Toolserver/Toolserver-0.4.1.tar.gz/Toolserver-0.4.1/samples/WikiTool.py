"""

Toolserver Framework for Python - Simple Wiki

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
import re

from Toolserver.Context import context
from Toolserver.Tool import registerTool, StandardTool
from Toolserver.Utils import logWarning, logError
from Toolserver.Utils import NotFoundError, ForbiddenError, RedirectError
from Toolserver.Utils import parseQueryFromRequest, parseQueryFromString
from Toolserver.TagRenderer import html

pageTemplate = html.html(
	html.head(html.title('%(title)s')),
	html.body(
		html.p(
			html.a('edit', href='%(edit)s'),
			align='right'
		),
		html.h1('%(title)s'),
		html.p('%(body)s')
	)
)

pageEditTemplate = html.html(
	html.head(html.title('%(title)s')),
	html.body(
		html.p(
			html.a('view', href='%(view)s'),
			align='right'
		),
		html.form(
			html.input(name='name', type='hidden', value='%(name)s'),
			html.p(html.input(name='title', value='%(title)s')),
			html.p(html.textarea('%(text)s', name='text')),
			html.p(html.input(name='submit', type='submit', value='Submit'), align='right'),
		)
	)
)

# precompiled regular expressions
LINK = re.compile(r'\[\[([^\]]*)\]\]')
ILLEGAL = re.compile(r'[^a-zA-Z0-9\-\_\+]+')

class WikiTool(StandardTool):

	# all content is HTML with the tool
	_content_type = 'text/html'

	# define types for WSDL generation
	_types = StandardTool._types + (
		('stringList', ['xsd:string']),
		('pageType', {'name': 'xsd:string', 'title': 'xsd:string', 'paras': 'typens:stringList'})
	)

	# this private method finds a page and returns it's link
	# (or it's creation link, if the page doesn't exist)
	def _findPage(self, title):
		name = ILLEGAL.sub(lambda m: '', title)
		if self._exists('%s.txt' % name):
			return self._getNameAsPath() + name + '.html'
		else:
			return self._getMethodAsPath('getPage', name=name)

	# this private method rewrites page links
	def _rewriteLinks(self, page):
		for i in range(0, len(page['paras'])):
			page['paras'][i] = LINK.sub(
				lambda m: html.a(m.group(1), href=self._findPage(m.group(1)))
				}, page['paras'][i]
			)

	# this private method loads a wiki page from a file
	def _loadPage(self, pagename):
		content = self._load('%s.txt' % pagename)
		paragraphs = content.split('\n\n')
		header = paragraphs[0].split('\n')
		del paragraphs[0]
		res = {'paras': paragraphs, 'name':pagename}
		for h in header:
			(var, val) = h.split(': ', 1)
			res[var] = val
		return res
	
	# this private method stores a wiki page to a file
	def _storePage(self, page):
		content = ''
		for h in ('title',):
			content += '%s: %s\n' % (h, page.get(h,''))
		content += '\n'
		content += '\n\n'.join(page['paras'])
		self._store('%s.txt' % page['name'], content)
	
	# this private method renders a wiki page
	def _renderPage(self, page):
		self._rewriteLinks(page)
		body = '<p>'.join(page.get('paras',()))
		content = pageTemplate % {
			'edit': self._getMethodAsPath('getPage', name=page['name']),
			'title': page['title'],
			'body': body
		}
		self._store('%s.html' % page['name'], content)
	
	# this method checks wether the start page exists or doesn't
	# exist. If it doesn't exist, the user is redirect to the
	# edit page for the start page, otherwise he is redirected to the
	# start page itself. This method is only called via REST style API
	def index(self, request, data):
		if self._exists('start.txt'):
			raise RedirectError(self._getNameAsPath()+'start.html')
		else:
			raise RedirectError(self._getMethodAsPath('getPage', name='start'))

	def index_validate_RPC(self, *args, **kw):
		raise ForbiddenError()

	def updatePage(self, pagename, title, text):
		"""
		this method updates an existing page. It can be used via REST
		to update a page. It will redirect to the page editor if used
		via REST.
		"""
		page = {
			'name': pagename,
			'title': title,
			'paras': text.split('\n\n')
		}
		self._storePage(page)
		return self._async(self._renderPage, page)
	
	updatePage_signature = ('xsd:string', 'xsd:string', 'xsd:string', 'xsd:string')
	
	def updatePage_parser(self, request, data):
		if request.command in ('GET', 'HEAD'):
			form = parseQueryFromRequest(request)
		elif request.command in ('POST', 'PUT'):
			form = parseQueryFromString(data)
		else:
			raise NotImplementedError()
		context.form = form
		return ((form['name'][0], form['title'][0], form['text'][0]), {})
	
	def updatePage_generator(self, request, result):
		raise RedirectError(self._getMethodAsPath('getPage', name=context.form['name'][0]))
		
	
	def getPage(self, pagename):
		"""
		this method returns a page as structured element
		ready for editing. If used via REST it will produce
		a edit form.
		"""
		if self._exists('%s.txt' % pagename):
			return self._loadPage(pagename)
		else:
			return {
				'name': pagename,
				'title': 'Put your Title here',
				'paras': []
			}
	
	getPage_signature = ('typens:pageType', 'xsd:string')
	
	def getPage_parser_GET(self, request, data):
		form = parseQueryFromRequest(request)
		return ((form['name'][0],), {})
	
	def getPage_generator_GET(self, request, result):
		return pageEditTemplate % {
			'update': self._getMethodAsPath('updatePage'),
			'view': self._getNameAsPath() + result['name'] + '.html',
			'name': result['name'],
			'title': result['title'],
			'text': '\n\n'.join(result['paras'])
		}

registerTool(WikiTool, 'wiki')

