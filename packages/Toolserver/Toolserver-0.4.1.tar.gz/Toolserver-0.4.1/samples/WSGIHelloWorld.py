# Just move this to your $HOME/.Toolserver/wsgi/ directory if you have
# wsgiref installed and restart your toolserver. The access the URL
# http://<serverhostname>:<serverport>/WSGI/test

def old_app(environ, start_response):
	status = '200 ALLES OK'
	response_headers = [('Content-type','text/plain')]
	write = start_response(status, response_headers)
	write('Hello World!\n')
	write('Done!\n')
	return []

def simple_app(environ, start_response):
	status = '200 ALLES OK'
	response_headers = [('Content-type','text/plain')]
	start_response(status, response_headers)
	return ['Hello world!\n']

class complex_app:

	def __init__(self, environ, start_response):
		self.environ = environ
		self.start = start_response

	def __iter__(self):
		status = '200 LOS GEHTS'
		response_headers = [('Content-type','text/plain')]
		self.start(status, response_headers)
		yield ("Hello %s!\n\n" % self.environ.get('REMOTE_USER', 'anonymous'))
		for i in range(0,10):
			yield ("This is line %s of 10\n" % i)
		yield ("Done!\n")

# This is the only TooFPy special change to enable WSGI applications.
# Everything else should be standard.
registerWSGI('test', simple_app)
registerWSGI('test2', complex_app)
registerWSGI('test3', old_app)

