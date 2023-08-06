"""

Toolserver Framework for Python - Challange Response Authentication Module

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
import hashlib
import time
import random

from Toolserver.Tool import StandardTool, getTool, hasTool, hasToolMethod
from Toolserver.Utils import ForbiddenError, logWarning
from Toolserver.Config import config

class CRAMTool(StandardTool):

	"""
	This base class gives you methods to get authentication tokens and
	provides methods to check those tokens. Tokens are built on
	challenges. You fetch challenges from the server (up to the number
	of calls you will do now) and create a token out of a challenge
	by passing in a tuple of the challenge and the response. The response
	is a hexstring of the SHA1 digest that is built by feeding first
	the challenge and second the secret.

	Tools that want to provide CRAM authentication need to have a
	config attribute named secret that must contain the tools secret
	to use for authentication. The secret itself is never transferred
	over the wire. Additionally those tools need to have a config
	attribute lifetime that defines the maximum lifetime for a
	challenge. The default for lifetime is 300 seconds, the default
	for secret is a random number, so you must overwrite that in
	your _defaults from a config file to make use of CRAM.
	"""

	def __init__(self, name, **kw):
		StandardTool.__init__(self, name, **kw)
		self._challenges = {}

	def _defaults(self):
		"""
		These are defaults for the configuration of this tool. To
		override these values, just create ServermanagerConfig.py in
		your ~/.Toolserver/etc/ path and just fill it with lines like

		secret = 'your secret for CRAM'
		lifetime = 300

		On server start this file will be automatically imported
		and all variables that correspond with defaults defined
		here will be overwritten with values from the configuration.
		"""
		StandardTool._defaults(self)
		self.config.secret = ''
		self.config.lifetime = 300

	# These are type declarations for WSDL generation. If you refer to
	# types you define yourself, use the typens: namespace. If you refer
	# to system defined types, use the xsd: namespace!
	_types = StandardTool._types + (
		('challengeList', ['xsd:string']),
	)

	def getChallenges(self, number):
		"""
		This method returns a list of authentication challenges. The
		max number of authentication challenges you can get with one
		call is limited to 10. Tokens are only valid throughout one
		server instantiation and can only be used once. Challenges are
		limited in their lifetime by the tool that creates the
		challenges.

		Python code to create the token interactively:

		>>> import hashlib
		>>> ctx = hashlib.sha1()
		>>> ctx.update(challenge)
		>>> ctx.update(secret)
		>>> print ctx.hexdigest()


		"""
		liste = []
		for i in range(0, number):
			challenge = self._getChallenge()
			liste.append(challenge)
		return liste
	
	getChallenges_signature = ('typens:challengeList', 'xsd:int')

	def getChallenges_validate_RPC(self, number):
		return 0

	def getChallenges_pre_condition(self, number):
		assert type(number) == type(1), 'the number must be an integer'
		assert number >= 1 and number <= 10, 'the number must be between 1 and 20'
	
	def getChallenges_post_condition(self, result):
		assert type(result) == type([]), 'result must be an array'
		for row in result:
			assert type(row) in (type(''), type(u'')), 'result must be an array of strings'
	
	def _getChallenge(self, *args):
		"""
		This is a helper method that creates challenges for your
		tool. The args passed in are used for constructing the
		challenge.
		"""
		ctx = hashlib.sha1()
		for i in args:
			ctx.update(str(i))
		ctx.update(str(os.getpid()))
		ctx.update(str(time.time()))
		ctx.update(repr(self))
		ctx.update(str(random.random()))
		challenge = ctx.hexdigest()
		self._challenges[challenge] = time.time()+self.config.lifetime
		return challenge
	
	def _createToken(self):
		"""
		This is a helper method that creates a token out of
		a challenge. This is for one-off tokens - they are not
		kept track of!
		"""
		assert self.config.secret, "no secret defined"
		ctx = hashlib.sha1()
		ctx.update(str(os.getpid()))
		ctx.update(str(time.time()))
		ctx.update(str(random.random()))
		challenge = ctx.hexdigest()
		ctx = hashlib.sha1()
		ctx.update(challenge)
		ctx.update(self.config.secret)
		return (challenge, ctx.hexdigest())
	
	def _checkToken(self, token):
		"""
		This is a helper method to check a token for validity.
		Regardless on wether the check succeeds or not, the
		challenge is removed from the challenge cache. If anything
		is wrong with the token, an exception is thrown.
		"""
		assert self.config.secret, "no secret defined"
		(challenge, response) = token
		if not self._challenges.has_key(challenge):
			logWarning("Challenge not known to me")
			raise ForbiddenError('Challenge not know to me')
		lifetime = self._challenges[challenge]
		del self._challenges[challenge]
		if lifetime < time.time():
			logWarning("Challenge expired")
			raise ForbiddenError('Challenge expired')
		ctx = hashlib.sha1()
		ctx.update(challenge)
		ctx.update(self.config.secret)
		if ctx.hexdigest() != response:
			logWarning("Response invalid")
			raise ForbiddenError('Response invalid')
		return challenge

class OnlyRPCCRAMTool(CRAMTool):

	"""
	This base class builds on CRAMTool but only allows RPC style access.
	Additionally the token is expected in the first parameter to every
	method and is automatically checked.
	"""

	def _validate_RPC(self, token, *args, **kw):
		self._checkToken(token)

	def _validate(self, request, user, password):
		raise ForbiddenError('REST access not allowed')
	
