import sys
import simpleweb.app
import simpleweb.utils


def cgi(urls, config):
	from wsgiref.handlers import CGIHandler
	wsgiapp = simpleweb.app.SimplewebApp(urls, config)
	CGIHandler().run(wsgiapp)

def fcgi(urls, config):
	from flup.server.fcgi import WSGIServer

	wsgiapp = simpleweb.app.SimplewebApp(urls, config)
	WSGIServer(wsgiapp, debug=config.enable_debug).run()

def development(urls, config):
	import memento
	import simpleweb.webserver

	if config.server_reload:
		#TODO: shouldn't we also be reloading 'models.' here?
		#it seems to work fine so far though, since, they show up as 'controllers.models.'
		wsgiapp = memento.Assassin("simpleweb.app:SimplewebReloadingApp()", ["controllers", "urls", "simpleweb", "config"])
	else:
		wsgiapp = simpleweb.app.SimplewebApp(urls, config)

	simpleweb.webserver.wsgiserve(
			wsgiapp, 
			config.server_host, 
			config.server_port, 
			config.server_reload,
			config.server_user, 
			config.server_group
			)

