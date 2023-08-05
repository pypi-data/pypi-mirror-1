"""
A simple, highly pluggable RESTafarian web framework, built by reusing known components

In simpleweb, the underlying priciple small applications that do one thing and do it well.
Each url is mapped to a single module which should contain the application entrypoint. This
means that while the application can be spread over various modules, it should have the main
methods (GET, POST, PUT, DELETE), in one file that the url is mapped to.

For instance:

urlmap('/user[/[{id}[/]]]', 'crm.users')
urlmap('/client[/[{id}[/]]]', 'crm.client')
urlmap('/blog[/[{id}[/]]]', 'blogengine.blog')
urlmap('/blog/{id}/comment[/[{id}[/]]]', 'blogengine.comment')

Each of the url handlers (aka controllers) do just one thing only, 
they publish the methods for GET, POST, PUT and DELETE. They are obviously
part of packages in this instance, but they *should* be refactored to make wholesome
sense in the api they publish.
"""
import sys, os

from middleware import StaticMiddleware, AuthMiddleware
from flup.middleware.session import DiskSessionStore, SessionMiddleware

import plugins.template
import plugins.dblayer
import utils
import dispatcher
import settings
import urls


__all__ = [
		'urladd', 
		'start',
		'run'
		]

urladd = urls.urladd



def start(config, method):
	app = urls.geturls()

	#TODO: make middleware stack configurable
	app = StaticMiddleware(app, config.dirname)
	#TODO: make auth middleware plug-able
	if hasattr(config, 'auth_plugin'):
		app = AuthMiddleware(app, authuser_class=config.auth_plugin.authuser_class)
	#TODO: add config attributes to control session initialization (e.g config.session_timeout)
	if config.use_session:
		app = SessionMiddleware(DiskSessionStore(), app)

	if method == 'cgi':
		from wsgiref.handlers import CGIHandler
		CGIHandler().run(app)
	elif method == 'fcgi':
		from flup.server.fcgi import WSGIServer
		WSGIServer(app, debug=config.debug).run()
	else:
		from wsgiref.simple_server import make_server
		print "Serving HTTP on %s port %s..." % (config.host, config.port)
		make_server(config.host, config.port, app).serve_forever()


def run(method=None):
	config = settings.Config("config")
	#TODO: make this use pkg_resources later
	config.dirname = os.path.dirname(config.__file__)

	if not hasattr(config, 'port') or str(getattr(config, 'port')).strip() == '' or getattr(config, 'port') is None:
		config.port = 8080

	if not hasattr(config, 'host'):
		config.host = '127.0.0.1'

	if not hasattr(config, 'debug'):
		config.debug = False

	if not hasattr(config, 'use_session'):
		config.use_session = False

	start(config, method)
