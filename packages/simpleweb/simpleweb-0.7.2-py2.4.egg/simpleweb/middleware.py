from simpleweb.extlib import static
import simpleweb.utils
import plugins.auth
import traceback

class StaticMiddleware(object):
	def __init__(self, app, root, static_url='/static/'):
		self.app = app
		self.static_url = static_url
		self.root = root
		self.cling = static.Cling(root)

	def __call__(self, environ, start_response):
		path_info = environ.get('PATH_INFO', '')
		if path_info.startswith(self.static_url):
			return self.cling(environ, start_response)
		else:
			return self.app(environ, start_response)

class AuthMiddleware(object):
	def __init__(self, app, session_key=simpleweb.utils.ENV_KEY_FLUP_SESSION, authuser_class=plugins.auth.AuthUser):
		self.app = app
		self.session_key = session_key
		self.authuser_class = authuser_class


	def __call__(self, environ, start_response):
		if self.session_key in environ:
			session = environ[self.session_key].session
			session.user = session.get(simpleweb.utils.ENV_KEY_AUTH_MIDDLEWARE, self.authuser_class())

		return self.app(environ, start_response)

class SimpleErrorMiddleware(object):
	def __init__(self, app, debug=False, msg=None):
		self.app = app
		self.debug = debug
		if not msg:
			self.msg = "An error has occured"
		else:
			self.msg = msg

	def __call__(self, environ, start_response):
		try:
			return self.app(environ, start_response)
		except Exception, e:
			start_response('500 Internal Server Error', [('Content-type','text/html')])
			if self.debug:
				self.msg = traceback.format_exc()

			return """
<h1>500 Internal Server Error</h1>

<p>
%s
</p>
""" % (self.msg.replace('\n', '<br/>'))
