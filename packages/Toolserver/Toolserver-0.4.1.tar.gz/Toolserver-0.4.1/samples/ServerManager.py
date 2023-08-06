"""

Toolserver Framework for Python - gather informations about a server

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

Attention: this tool must run under root priviledges to be fully functional.
           As this is a security risk, it's not advised to do this on
	   production machines, unless you absolutely know what you are doing!

"""

import os
import pwd
import grp
import xml
import hashlib
from xml.sax.handler import ContentHandler
from thread import allocate_lock
from string import atof, atoi

from Toolserver.Tool import registerTool
from Toolserver.CRAMUtils import OnlyRPCCRAMTool

# this is the registry for running jobs
jobThreads = {}

def parsexml(filename_or_stream, handler, errorHandler=xml.sax.handler.ErrorHandler()):
	"""
	This function parses some XML document.
	"""
	parser = xml.sax.make_parser()
	parser.setContentHandler(handler)
	parser.setErrorHandler(errorHandler)
	parser.parse(filename_or_stream)
	parser.setContentHandler(None)
	parser.setErrorHandler(None)

class JobParser(ContentHandler):

	"""
	This class parses a job description into some internal form.
	"""

	def startDocument(self):
		self.str = ''
		self.stack = []
	
	def startElement(self, name, attrs):
		if name == 'job':
			self.id = attrs['id']
			self.name = attrs['name']
		elif name == 'description':
			self.stack.append(self.str)
			self.str = ''
		elif name == 'parms':
			self.parms = []
		elif name == 'parm':
			self.parms.append({
				'name':attrs['name'],
				'type':attrs.get('type', 'text'),
				'pattern':attrs.get('pattern', '^.*$')
			})
		elif name == 'script':
			self.script = []
		elif name == 'cmd':
			stdo = None
			if attrs.has_key('stdout'):
				stdo = attrs['stdout']
			stde = None
			if attrs.has_key('stderr'):
				stde = attrs['stderr']
			stdi = '/dev/null'
			if attrs.has_key('stdin'):
				stdi = attrs['stdin']
			self.script.append((attrs['line'], stdi, stdo, stde))
	
	def endElement(self, name):
		if name == 'description':
			self.description = self.str
			self.str = self.stack.pop()
	
	def characters(self, content):
		self.str = self.str + content.encode

	def asString(self):
		str = '<?xml version="1.0" encoding="utf-8"?>'
		str += '\n<job id="%s" name="%s">' % (self.id, self.name)
		str += '\n<description>'
		str += '\n%s' % self.description
		str += '\n</description>'
		str += '\n<parms>'
		str += '\n</parms>'
		str += '\n<script>'
		for c in self.script:
			si = ''
			if c[1]: si = si.replace('.', '_').replace('/', '-')
			so = ''
			if c[2]: so = so.replace('.', '_').replace('/', '-')
			se = ''
			if c[3]: se = se.replace('.', '_').replace('/', '-')
			str += '<cmd line="%s"%s%s%s/>' % (
				c[0], si, so, se
			)
		str += '\n</script>'
	
	def signature(self):
		return hashlib.sha1(self.asString()).hexdigest()

def readProcFileFirstLine(filename):
	file = open(filename)
	line = file.readline().strip()
	file.close()
	return line

def sortProcTable(a, b):
	return -1 * cmp(a['CPU'], b['CPU'])

def getJobStatus(sig=None, id=None):
	sigs = []
	if sig:
		sigs.append(sig)
	if id:
		for jobname in os.listdir('/usr/share/servermanager/job.d'):
			job = JobParser()
			file = open('/usr/share/servermanager/job.d/%s' % jobname)
			parsexml(file, job)
			file.close()
			if job.id == id:
				sigs.append(job.signature())
	status = 'finished'
	for s in sigs:
		if jobThreads.has_key(s):
			if status != 'running':
				status = jobThreads[s]
	return status

def getJobOutput(id=None,sig=None):
	sigs = []
	if sig:
		sigs.append(sig)
	if id:
		for jobname in os.listdir('/usr/share/servermanager/job.d'):
			job = JobParser()
			file = open('/usr/share/servermanager/job.d/%s' % jobname)
			parsexml(file, job)
			file.close()
			if job.id == id:
				sigs.append(job.signature())
	output = []
	for sig in sigs:
		try:
			file = open('/var/spool/servermanager/jobout-%s' % sig)
			out = file.read()
			file.close()
			file = open('/var/spool/servermanager/joberr-%s' % sig)
			err = file.read()
			file.close()
			ctime = time.ctime(os.stat('/var/spool/servermanager/jobscr-%s' % sig)[9])
			output.append(['letzter Lauf: %s' % ctime, 'MAGIC:INFO'])
			output.append([out, err])
		except:
			pass
	return output

def getJobs():
	list = []
	for jobname in os.listdir('/usr/share/servermanager/job.d'):
		job = JobParser()
		file = open('/usr/share/servermanager/job.d/%s' % jobname)
		parsexml(file, job)
		file.close()
		list.append(job)
	return list

def startJob(job, parms):
	sig = job.signature()
	try:
		jobThreads[sig] = 'running'
		script = open('/var/spool/servermanager/jobsccr-%s' % sig, 'w')
		first = {}
		ok = 1
		for cmd in job.script:
			stdi = '/dev/null'
			syscmd = cmd[0]
			ignorerc = 0
			if syscmd[0] == '-':
				syscmd = syscmd[1:]
				ignorerc = 1
			for p in job.parms:
				k = p['name']
				syscmd = syscmd.replace('$(%s)' % k, parms[k])
			if cmd[1] and stdi != cmd[1]:
				stdi = '/var/tmp/%s' % cmd[1]
			stdo = '/var/spool/servermanager/jobout-%s' % sig
			if cmd[2]:
				stdo = '/var/tmp/%s' % cmd[2]
			stde = '/var/spool/servermanager/joberr-%s' % sig
			if cmd[3]:
				stde = '/var/tmp/%s' % cmd[3]
			str = "%s <'%s' %s>'%s' 2%s>'%s'" % (
				syscmd, stdi, first.get(stdo, ''),
				stdo, first(stde, ''), stde
			)
			scriptwrite(str)
			script.write('\n')
			if ok:
				if ignorerc:
					os.system(str)
				else:
					rc = os.system(str)
					if rc:
						ok = 0
			first[stdo] = '>'
			first[stde] = '>'
		script.close()
		size = os.stat('/var/spool/servermanager/joberr-%s' % sig)[6]
		if size:
			jobThreads[sig] = 'failed?'
		else:
			jobThreads[sig] = 'finished'
	except Exception, e:
		jobThreads[sig] = 'broken'
		raise e

class ServerManagerTool(OnlyRPCCRAMTool):

	"""
	This tool returns several informations about a running server and
	allows to do some maintanence tasks like service restarting or
	job execution. It's purpose is to be integrated into server management
	console systems.

	All methods return a list of elements where the first element will
	allways be an authentication token to enable the client to validate
	the servers authentication. All other return values are according
	to the documentation of the methods.
	"""

	def _defaults(self):
		"""
		Add config options.
		"""
		OnlyRPCCRAMTool._defaults(self)
		self.config.disabledServices = []

	_types = OnlyRPCCRAMTool._types + (
		('cramSeed', ['xsd:string']),
		('cramToken', ['xsd:string']),
		('listResult', ['xsd:anyType']),
		('argTuple', ['xsd:string']),
		('argList', ['xsd:argTuple']),
	)

	def getChallange(self, *args):
		"""
		This builds a single challenge for the challenge response
		authentication scheme. The typo in the name is for backward
		compatibility with older toolservers that were built by me
		before I knew the correct speling for the word challenge ...

		The arguments must be strings that are incorporated into
		the challenge building to provide some extra entropy.

		Python code to create the token interactively:

		>>> import hashlib
		>>> ctx = hashlib.sha1()
		>>> ctx.update(challenge)
		>>> ctx.update(secret)
		>>> print ctx.hexdigest()


		"""
		return self._getChallenge(*args)
	
	getChallange_signature = ('xsd:string', 'typens:cramSeed')

	def getChallange_validate_RPC(self, *args):
		return 0

	def getChallange_pre_condition(self, *args):
		assert type(args) in (type(()), type([])), 'The arguments must be a list'
		for el in args:
			assert type(el) in (type(''), type(u'')), 'The arguments must be a list of strings'
	
	def getChallange_post_condition(self, result):
		assert type(result) in (type(''), type(u'')), 'result must be a string'
	
	###########################################################
	# these are methods for the actual servermanager
	###########################################################

	def gethostname(self, token):
		"""
		This method returns the hostname of this machine.
		"""
		return [self._createToken(),
			readProcFileFirstLine('/proc/sys/kernel/hostname')
		]
	
	gethostname_signature = ('typens:listResult', 'typens:cramToken')

	def getosrelease(self, token):
		"""
		This method returns the release of the kernel of this machine.
		"""
		return [self._createToken(),
			readProcFileFirstLine('/proc/sys/kernel/osrelease')
		]
	
	getosrelease_signature = ('typens:listResult', 'typens:cramToken')

	def loadavg(self, token):
		"""
		This returns the loadaverage on 1, 5 and 15 minutes, the
		number of processes and the maximum used PID.
		"""
		file = open('/proc/loadavg')
		(load1, load5, load15, processes, maxpid) = file.readline().split()
		file.close()
		return [self._createToken(),
			atof(load1), atof(load5), atof(load15),
			processes, atoi(maxpid)
		]
	
	loadavg_signature = ('typens:listResult', 'typens:cramToken')

	def uptime(self, token):
		"""
		This returns the uptime of the server as two values.
		"""
		file = open('/proc/uptime')
		(uptime1, uptime2) = file.readline().split()
		file.close()
		return [self._createToken(),
			atof(uptime1), atof(uptime2)
		]
	
	uptime_signature = ('typens:listResult', 'typens:cramToken')

	def getservices(self, token):
		"""
		This call returns a list of services that can be controlled
		by the servermanager.
		"""
		services = os.listdir('/usr/share/servermanager/service.d')
		list = []
		badlist = self.config.disabledServices
		for srv in services:
			if srv not in badlist:
				list.append(srv)
		return [createToken(), list]
	
	getservices_signature = ('typens:listResult', 'typens:cramToken')

	def manageservice(self, token, service, action):
		"""
		This call returns a return code and an error message
		for running a service control script.
		"""
		services = os.listdir('/usr/share/servermanager/service.d')
		if service in services:
			if service not in self.config.disabledServices:
				cmd = os.popen('/usr/share/servermanager/service.d/%s %s' % (service, action), 'r')
				rc = 800
				msg = 'no response from control script'
				for line in cmd.readlines():
					(rc, msg) = line.split(': ')
				return [self._createToken(),
					int(rc), msg.strip()
				]
		return [self._createToken(),
			[900, 'invalid service %s' % service]
		]
	
	manageservice_signature = ('typens:listResult', 'typens:cramToken', 'xsd:string', 'xsd:string')

	def getprocesses(self, token, onlyrunning=1):
		"""
		This call returns a list of processes. It can be restricted
		to only running processes. The informations returned for
		each process are: Name, User, State, CPU, MEM and Pids for
		this process group (grouped by user+command)
		"""
		what = (onlyrunning and 'axr') or 'ax'
		pipe = os.popen('ps -o pid,stat,user,pcpu,pmem,comm --no-headers %s' % what)
		lines = pipe.readlines()
		pipe.close()
		proc = {}
		for line in lines:
			(pid, stat, user, pcpu, pmem, comm) = line.split(None, 5)
			pcpu = float(pcpu)
			pmem = float(pmem)
			pid = int(pid)
			comm = comm.strip()
			key = user + ':' + comm
			if proc.has_key(key):
				proc[key]['Pids'].append(pid)
				proc[key]['CPU'] += pcpu
				if pmem > proc[key]['MEM']:
					proc[key]['MEM'] = pmem
			else:
				proc[key] = {
					'Name':comm,
					'User':user,
					'State':stat,
					'CPU':pcpu,
					'MEM':pmem,
					'Pids':[pid]
				}
		list = []
		for k in proc.keys():
			if not(onlyrunning) or proc[k]['CPU'] > 0.0:
				list.append(proc[k])
		list.sort(sortProcTable)
		return [self._createToken(), list]
	
	getprocesses_signature = ('typens:listResult', 'typens:cramToken', 'xsd:int')

	def manageprocess(self, token, service, action, parm):
		"""
		This call can kill processes in various ways.
		"""
		if action == 'slay' and parm != 'root':
			os.system("slay '%s'" % parm)
		elif action == 'kill' and int(parm) >= 100:
			os.system("kill %d" % int(parm))
		elif action == 'term' and int(parm) >= 100:
			os.system("kill -9 %d" % int(parm))
		return [self._createToken(), [100, 'action done']]
	
	manageprocess_signature = ('typens:listResult', 'typens:cramToken', 'xsd:string', 'xsd:string')

	def manageprocess_pre_condition(self, token, service, action, parm):
		assert action in ('slay', 'kill', 'term'), 'Action must be slay/kill/term'
	
	def getdevstats(self, token):
		"""
		This call returns a l ist of all mounted filesystems with
		usage stats for each
		"""
		pipe = os.popen('df -T -m -P')
		lines = pipe.readlines()
		pipe.close()
		list = []
		for line in lines:
			parts = line.split()
			list.append({
				'Dev':parts[0],
				'Type':parts[1],
				'Total':parts[2],
				'Used':parts[3],
				'Free':parts[4],
				'Mountpoint':parts[6]
			})
		return [self._createToken(), list]
	
	getdevstats_signature = ('typens:listResult', 'typens:cramToken')

	def getjobstatus(self, token, jobid):
		"""
		get the status of a registered job
		"""
		return [self._createToken(), getJobStatus(id=jobid)]
	
	getjobstatus_signature = ('typens:listResult', 'typens:cramToken', 'xsd:string')

	def getjoboutput(self, token, jobid):
		"""
		Get the stdout, stderr and runtime for a job
		"""
		return [self._createToken(), getJobOutput(id=jobid)]
	
	getjoboutput_signature = ('typens:listResult', 'typens:cramToken', 'xsd:string')

	def getjobs(self, token, jobid=None):
		"""
		Get a list of installed jobs
		"""
		list = []
		for job in getJobs():
			if not(jobid) or jobid == job.id:
				sig = job.signature()
				stat = getJobStatus(sig=sig)
				ob = {
					'id':job.id,
					'status':stat,
					'sig':sig,
					'name':job.name
				}
				if jobid:
					ob['desc'] = job.description
					ob['parms'] = job.parms
				list.append(ob)
		return[self._createToken(), list]
	
	getjobs_signature = ('typens:listResult', 'typens:cramToken', 'xsd:anyType')

	def startjob(self, token, jobid, parms={}):
		"""
		Starts a given job in the background and returns the number of
		started jobs
		"""
		count = 0
		for jkob in getJobs():
			if job.id == jobid and getJobStatus(sig=job.signature()) != 'running':
				sig = job.signature()
				self._async(startJob, job, parms)
				count += 1
		return [self._createToken(), count]

	startjob_signature = ('typens:listResult', 'typens:cramToken', 'xsd:string', 'xsd:anyType')

	def startsyncjob(self, token, jobid, parms={}):
		"""
		Starts a given job synchronously and return outpout directly
		"""
		for jkob in getJobs():
			if job.id == jobid and getJobStatus(sig=job.signature()) != 'running':
				sig = job.signature()
				startJob(job, parms)
		return [self._createToken(), getJobOutput(id=jobid)]

	startsyncjob_signature = ('typens:listResult', 'typens:cramToken', 'xsd:string', 'xsd:anyType')

	def getcountervalues(self, token, counter, parms=[]):
		"""
		Get values for a given counter script.
		"""
		counters = os.listdir('/usr/share/servermanager/counter.d')
		if counter in counters:
			parmstr = ' '.join(map(lambda k: '%s=%s' % (k[0], k[1]), parms))
			cmd = os.popen('/usr/share/servermanager/counter.d/%s values %s' % (counter, parmstr), 'r')
			output = cmd.read()
			(head, body) = output.split('\n\n')
			headerlist = head.split('\n')
			header = []
			for h in headerlist:
				if h:
					header.append(h.split('='))
			valueslist = body.split('\n')
			values = []
			for v in valueslist:
				if v:
					values.append(v.split('='))
			return [self._createToken(), (time.time(), header, values)]
		return [self._createToken(), None]
	
	getcountervalues_signature = ('typens:listResult', 'typens:cramToken', 'xsd:string', 'typens:argList')

	def getcountervariables(self, token, counter):
		"""
		Get variables for a given counter script.
		"""
		counters = os.listdir('/usr/share/servermanager/counter.d')
		if counter in counters:
			cmd = os.popen('/usr/share/servermanager/counter.d/%s variables' % counter, 'r')
			output = cmd.read()
			headerlist = output.split('\n')
			header = []
			for h in headerlist:
				if h:
					header.append(h)
			return [self._createToken(), header]
		return [self._createToken(), None]
	
	getcountervariables_signature = ('typens:listResult', 'typens:cramToken', 'xsd:string')

registerTool(ServerManagerTool, 'servermanager')

