"""

Toolserver Framework for Python - check mail addresses for validity

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
import smtplib
import DNS

from Toolserver.Context import context
from Toolserver.Tool import registerTool, StandardTool
from Toolserver.Utils import parseQueryFromRequest, parseQueryFromString
from Toolserver.TagRenderer import xml

# precompiled regular expressions
reParts = re.compile('^(.*)@(.*)$')
reDomain = re.compile('^(([0-9a-zA-Z]+-)*[0-9a-zA-Z]+\\.)+([0-9a-zA-Z]+-)*[0-9a-zA-Z]+$')
reUser = re.compile('^[^<>\\(\\)\\[\\],;:@\x01-\x20\x7f-\xff]+$')

class MailCheckTool(StandardTool):

	"""
	This tool checks mail addresses for validity. This is a very simple
	service for public use. It should run on a server with static
	connectivity, as some servers deny communication with dynamic
	IP addresses (for example AOL does this).
	"""

	def _defaults(self):
		"""
		These are defaults for the configuration of this tool.
		To override these values, just create a file MailcheckConfig.py
		in your ~/.Toolserver/etc/ path and just fill it with lines
		like

		myname = 'your-real.hostname.here'
		good_domains = (
			'some-real.good.domain',
			'some-other-real.good.domain'
		)
		bad_domains = (
			'some-real.bad.domain',
		)

		On server start this file will be automatically imported
		and all variables that correspond with defaults defined
		here will be overwritten with values from the configuration.
		"""
		self.config.myname = 'your.hostname.here'
		self.config.good_domains = (
			'leica-users.org',
		)
		self.config.bad_domains = (
		)

	_types = StandardTool._types + (
		('checkResult', {
			'valid': 'xsd:int',
			'level': 'xsd:int',
			'message': 'xsd:string'
		}),
	)

	def validateEmail(self, email):
		"""
		This method checks a given email address for validity.
		It does this by checking the overall syntax of the address
		and then checking via callback to the addresses MX servers
		wether any of the servers would accept this address as valid.
		Pass in the address as a string. The return value is a
		struct with two elements. The 'valid' element is either
		0 or 1 where 1 says the address is valid. The 'message'
		element carries a textual description of the problem. The
		'level' element carries a level for the given message. It's
		1 for temporary failures, 2 for permanent failures and 3
		for syntax errors. With valid addresses, the level is 0
		and the message is OK.
		"""
		res = reParts.match(email)
		if res:
			user = res.group(1)
			host = res.group(2)
			if user == '':
				return {
					'valid': 0,
					'level': 3,
					'message': 'Address missing user part',
				}
			if host == '':
				return {
					'valid': 0,
					'level': 3,
					'message': 'Address missing domain part',
				}
			if not(reDomain.match(host)):
				return {
					'valid': 0,
					'level': 3,
					'message': 'Invalid syntax for domain part'
				}
			if not(reUser.match(user)):
				return {
					'valid': 0,
					'level': 3,
					'message': 'Invalid syntax for user part'
				}

			if host in self.config.good_domains:
				return {
					'valid': 1,
					'level': 0,
					'message': 'OK'
				}

			if host in self.config.bad_domains:
				return {
					'valid': 0,
					'level': 2,
					'message': 'The domain is blacklisted'
				}

			mxhosts = DNS.mxlookup(host)
			msg = 'No MX accepted SMTP traffic'
			if len(mxhosts) == 0:
				mxhosts = [
					(10, host)
				]
				msg = 'Host did not accept SMTP traffic'
			for (level, server) in mxhosts:
				try:
					srv = smtplib.SMTP(server)
					try:
						(code, msg) = srv.helo(self.config.myname)
						if 200 <= code <= 299:
							(code, msg) = srv.docmd('MAIL FROM:', '<>')
							if 200 <= code <= 299:
								(code, msg) = srv.docmd('RCPT TO:', '<%s>' % email)
								if 200 <= code <= 299:
									return {
										'valid': 1,
										'level': 0,
										'message': 'OK'
									}
								elif 500 <= code <= 599:
									return {
										'valid': 0,
										'level': 2,
										'message': '%s (%s/%s)' % (msg, code, server)
									}
								else:
									return {
										'valid': 0,
										'level': 1,
										'message': '%s (%s/%s)' % (msg, code, server)
									}
					finally:
						srv.quit()
				except:
					(e, d, tb) = sys.exc_info()
					msg = repr(e)
			return {
				'valid': 0,
				'level': 1,
				'message': 'SMTP problem: %s' % msg
			}
		else:
			return {
				'valid': 0,
				'level': 3,
				'message': 'Invalid syntax for address'
			}

	def validateEmail_pre_condition(self, email):
		assert type(email) == type(''), 'email addresses must be ascii string'
	
	def validateEmail_post_condition(self, result):
		assert type(result) == type({})
		assert type(result.get('valid', None)) == type(1), 'validity flag must be integer'
		assert type(result.get('level', None)) == type(1), 'level must be integer'
		assert type(result.get('message', None)) == type(''), 'message must be ascii string'
		if result['valid']:
			assert result['level'] == 0, 'level for valid address must be 0'
			assert result['message'] == 'OK', 'message for valid address must be OK'
		else:
			assert result['level'] in (1,2,3), 'level for invalid address must be in 1..3'
			assert result['message'] != '', 'there must be a non-empty message for invalid addresses'

	validateEmail_signature = ('typens:checkResult', 'xsd:string')

registerTool(MailCheckTool, 'mailcheck')

DNS.DiscoverNameServers()
