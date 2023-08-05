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

import plugins.template
import plugins.dblayer
import utils
import dispatcher
import settings
import _urls
import app


__all__ = [
		'urladd', 
		'start',
		'run'
		]

urladd = _urls.urladd




def start(config, method):
	#TODO: think of how to make it such that we only get the function we want from 
	# the method plugins
	import plugins.runmethods
	runmethod = getattr(plugins.runmethods, method)
	runmethod(config)

def run(method='development'):
	config = settings.Config("config")
	#TODO: make this use pkg_resources later
	config.dirname = os.path.dirname(config.__file__)

	if not hasattr(config, 'port') or str(getattr(config, 'port')).strip() == '' or getattr(config, 'port') is None:
		config.port = 8080

	if not hasattr(config, 'host'):
		config.host = '127.0.0.1'

	if not hasattr(config, 'enable_debug'):
		config.enable_debug = False

	if not hasattr(config, 'enable_sessions'):
		config.enable_sessions = False

	start(config, method)
