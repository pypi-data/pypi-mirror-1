import selector,yaro
import simpleweb
import utils

class wrapper(yaro.Yaro):
	def __call__(self, environ, start_response):
		"""Create Request, call thing, unwrap results and respond."""

		if 'yaro.request' in environ:
			req = environ['yaro.request']
		else:
			req = yaro.Request(environ, start_response, self.extra_props)
			environ['yaro.request'] = req 

		#make session object available easily via request object
		if utils.ENV_KEY_FLUP_SESSION in environ:
			req.session = environ[utils.ENV_KEY_FLUP_SESSION].session

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
	def __init__(self, **kw):
		self.urls = selector.Selector(wrap=wrapper)
		self.urlmap = {}

	def add(self, url, controller):
		self.urlmap[url] = controller
		method_dict = simpleweb.utils.get_methods_dict(controller, ['GET', 'POST', 'PUT', 'DELETE'])
		self.urls.add(url, method_dict)

	def geturls(self):
		return self.urls

