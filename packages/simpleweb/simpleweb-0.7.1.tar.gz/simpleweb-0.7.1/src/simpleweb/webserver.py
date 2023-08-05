import sys
import os, pwd, grp
from wsgiref.simple_server import make_server

def _msg_info(msg):
	sys.stdout.write("=> %s\n" %(msg))

def _msg_err(msg):
	sys.stderr.write("!! %s\n" %(msg))

def wsgiserve(wsgiapp, host='127.0.0.1', port=8080, reload=True, user='nobody', group='nobody'):
	if reload:
		reload_status = 'On'
	else:
		reload_status = 'Off'

	server = make_server(host, port, wsgiapp)
		
	if os.geteuid() == 0: #only do this if we're root
		try:
			gid = grp.getgrnam(group)[2]
			uid = pwd.getpwnam(user)[3]
		except KeyError:
			_msg_err("Could not find the specified user/group on the system, ignoring and running as '%s'" %(pwd.getpwuid(os.geteuid())[0]))
			pass
		else:
			if os.name == 'posix':
				os.setgid(gid)
				os.setuid(uid)
	
	_msg_info("Now Serving on %s port %s [reloading = %s]..." % (host, port, reload_status))
	server.serve_forever()
