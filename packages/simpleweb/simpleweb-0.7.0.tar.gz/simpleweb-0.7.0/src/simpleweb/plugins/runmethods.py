import sys
import simpleweb._urls as _urls
import simpleweb.app

def cgi(config):
	from wsgiref.handlers import CGIHandler
	wsgiapp = simpleweb.app.SimplewebApp(_urls, config)
	CGIHandler().run(wsgiapp)

def fcgi(config):
	from flup.server.fcgi import WSGIServer
	wsgiapp = simpleweb.app.SimplewebApp(_urls, config)
	WSGIServer(wsgiapp, debug=config.enable_debug).run()

def development(config):
	from wsgiref.simple_server import make_server
	import os, pwd, grp
	wsgiapp = simpleweb.app.SimplewebApp(_urls, config)
	sys.stdout.write("=> Started Serving HTTP on %s port %s...\n" % (config.host, config.port))
	server = make_server(config.host, config.port, wsgiapp)
		
	if os.geteuid() == 0: #only do this if we're root
		try:
			gid = grp.getgrnam(config.group)[2]
			uid = pwd.getpwnam(config.user)[3]
		except AttributeError:
			#ignore
			pass
		else:
			if os.name == 'posix':
				os.setgid(gid)
				os.setuid(uid)
	
	server.serve_forever()
