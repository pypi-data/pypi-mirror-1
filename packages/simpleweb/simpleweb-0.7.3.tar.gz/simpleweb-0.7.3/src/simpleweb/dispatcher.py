from simpleweb.extlib import selector,yaro
import simpleweb.utils

class wrapper(yaro.Yaro):
	def __call__(self, environ, start_response):
		"""Create Request, call thing, unwrap results and respond."""

		if 'yaro.request' in environ:
			req = environ['yaro.request']
		else:
			req = yaro.Request(environ, start_response, self.extra_props)
			environ['yaro.request'] = req 

		#make session object available easily via request object
		if simpleweb.utils.ENV_KEY_FLUP_SESSION in environ:
			req.session = environ[simpleweb.utils.ENV_KEY_FLUP_SESSION].session

		body = self.app(req, **environ['selector.vars'])
		if body is None:
			body = req.res.body
		if not req.start_response_called:
			req.start_response(req.res.status, req.res._headers, req.exc_info)
		if isinstance(body, str):
			return [body]
		elif yaro.isiterable(body):
			return body
		else:
			return yaro.util.FileWrapper(body)

class Urls(object):
	def __init__(self):
		self.urls = selector.Selector(wrap=wrapper)
		self.urlmap = []

	def add(self, url, controller):
		self.urlmap.append((url, controller))

	def _setup(self):
		for url, controller in self.urlmap:
			try:
				method_dict = simpleweb.utils.get_methods_dict(controller, ['GET', 'POST', 'PUT', 'DELETE'])
			except ImportError, e:
				simpleweb.utils.msg_warn(str(e))
				continue
			self.urls.add(url, method_dict)

	def geturls(self):
		self._setup()
		return self.urls

