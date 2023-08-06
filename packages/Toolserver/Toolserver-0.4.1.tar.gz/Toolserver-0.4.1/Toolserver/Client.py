"""
Toolserver Framework for Python - abstract client for remote tools

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

from Toolserver.ClientMachinery import RemoteToolserver, documentEncoding

import Toolserver.SOAPClient
import Toolserver.XMLRPCClient
import Toolserver.PickleRPCClient

if __name__ == '__main__':
	import os
	import sys
	import getopt
	rsa = 0
	myname = 'localhost'
	host = 'localhost'
	port = 4334
	user = None
	password = None
	auth = None
	(opts, args) = getopt.getopt(sys.argv[1:], 'rs:h:p:u:w:m:')
	for (switch, value) in opts:
		if switch == '-r':
			rsa = 1
		elif switch == '-s':
			myname = value
		elif switch == '-h':
			host = value
		elif switch == '-p':
			port = value
		elif switch == '-u':
			user = value
		elif switch == '-w':
			password = value
		elif switch == '-m':
			auth = value
	method = 'RPC2'
	if len(args): method = args[0]
	srv = None
	kw = {}
	if method == 'SOAP':
		kw['simplify'] = 1
	elif method == 'PYRPC':
		rsa = 1
	if rsa:
		privkey = os.path.expanduser('~/.Toolserver/privkeys/localhost.key')
		pubkey = os.path.expanduser('~/.Toolserver/pubkeys/localhost.key')
		kw['pubkey'] = pubkey
		kw['privkey'] = privkey
		kw['localname'] = myname
	if auth == 'basic' and user and password:
		kw['basic'] = (user, password)
	srv = RemoteToolserver('http://%s:%s/' % (host, port), method, **kw)
	system = srv.getTool('system')
	print system.listRegisteredFunctions()

