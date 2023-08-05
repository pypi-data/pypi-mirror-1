import sys
from middleware import StaticMiddleware, AuthMiddleware, SimpleErrorMiddleware 
import simpleweb.utils

class SimplewebApp(object):
	def __init__(self, urls, config):
		self.wsgiapp = _create_app(urls, config)

	def __call__(self, environ, start_response):
		return self.wsgiapp(environ, start_response)

class SimplewebReloadingApp(object):
	def __call__(self, environ, start_response):
		import simpleweb._urls
		import simpleweb.settings

		urls = simpleweb._urls
		config = simpleweb.settings.Config("config")

		wsgiapp = _create_app(urls, config)
		wsgiapp = SimpleErrorMiddleware(wsgiapp, config.enable_debug, msg="An error has occured.\nFor a detailed traceback, enable debugging in config.py.\n You can do this by setting <pre >enable_debug = True</pre>")
		return wsgiapp(environ, start_response)
		

def _create_app(url, config):
	try:
		sys.path.insert(0, '.')
		__import__('urls')
	except ImportError, e:
		simpleweb.utils.msg_err("Could not successfully import urls.py: %s" % (e))
		sys.exit()

	app = url.geturls()

	#TODO: make middleware stack configurable
	app = StaticMiddleware(app, config.working_directory)
	#TODO: make auth middleware plug-able
	if hasattr(config, 'auth_plugin'):
		app = AuthMiddleware(app, authuser_class=config.auth_plugin.authuser_class)
	#TODO: add config attributes to control session initialization (e.g config.session_timeout)
	if config.enable_sessions:
		try:
			from flup.middleware.session import DiskSessionStore, SessionMiddleware
			app = SessionMiddleware(DiskSessionStore(), app)
		except ImportError:
			pass
	
	return app
