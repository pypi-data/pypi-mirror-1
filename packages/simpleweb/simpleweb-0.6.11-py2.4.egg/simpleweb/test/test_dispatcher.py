import dispatcher

def GET():
	return "GET"
	pass

class TestUrls(object):

	def test_add(self):
		urls = dispatcher.Urls()
		urls.add('/', 'test_dispatcher')
		print urls.urls.mappings
		assert urls.urls.mappings[0][1]['GET']

