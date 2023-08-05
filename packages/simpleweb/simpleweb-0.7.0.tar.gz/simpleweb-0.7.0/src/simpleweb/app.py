import sys
from flup.middleware.session import DiskSessionStore, SessionMiddleware
from middleware import StaticMiddleware, AuthMiddleware

class SimplewebApp(object):
	def __init__(self, urls, config):
		self.wsgiapp = _create_app(urls, config)

	def __call__(self, environ, start_response):
		return self.wsgiapp(environ, start_response)

def _create_app(url, config):
	try:
		sys.path.insert(0, '.')
		__import__('urls')
	except ImportError, e:
		sys.stderr.write("Could not successfully import urls.py. Details follow:\n\t%s\n" % (e))

	app = url.geturls()

	#TODO: make middleware stack configurable
	app = StaticMiddleware(app, config.dirname)
	#TODO: make auth middleware plug-able
	if hasattr(config, 'auth_plugin'):
		app = AuthMiddleware(app, authuser_class=config.auth_plugin.authuser_class)
	#TODO: add config attributes to control session initialization (e.g config.session_timeout)
	if config.enable_sessions:
		app = SessionMiddleware(DiskSessionStore(), app)

	app.modules = sys.modules.keys()
	return app

