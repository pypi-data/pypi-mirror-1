import sys
import simpleweb.app
import simpleweb.utils


def cgi(urls, config):
	from wsgiref.handlers import CGIHandler
	wsgiapp = simpleweb.app.SimplewebApp(urls, config)
	CGIHandler().run(wsgiapp)

def fcgi(urls, config):
	try:
		from flup.server.fcgi import WSGIServer
	except ImportError:
		simpleweb.utils.optional_dependency_err('FCGI WSGI server for "%s"' % (config.working_directory), 'flup')
	else:
		wsgiapp = simpleweb.app.SimplewebApp(urls, config)
		WSGIServer(wsgiapp, debug=config.enable_debug).run()

def development(urls, config):
	from simpleweb.extlib import memento
	import simpleweb.webserver

	if config.server_reload:
		#TODO: shouldn't we also be reloading 'models.' here?
		#it seems to work fine so far though, since, they show up as 'controllers.models.'
		wsgiapp = memento.Assassin("simpleweb.app:SimplewebReloadingApp()", ["controllers", "urls", "simpleweb", "config"])
	else:
		wsgiapp = simpleweb.app.SimplewebApp(urls, config)

	warnmsg = None
	
	if config.enable_sessions:
		try:
			import flup.middleware.session
		except ImportError:
			warnmsg = "'flup' not installed. Sessions will be unavailable"

	simpleweb.webserver.wsgiserve(
			wsgiapp, 
			config.server_host, 
			config.server_port, 
			config.server_reload,
			config.server_user, 
			config.server_group,
			warnmsg = warnmsg
			)

