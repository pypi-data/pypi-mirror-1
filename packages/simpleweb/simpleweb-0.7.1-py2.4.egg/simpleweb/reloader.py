from memento import Mori

class ReloaderMiddleware(Mori):
	def __init__(self, app, turn_on=False):

		Mori.__init__(self, None, turn_on)
		self.app = app

	def __call__(self, environ, start_response):
		self._reload()
		return self.app(environ, start_response)

