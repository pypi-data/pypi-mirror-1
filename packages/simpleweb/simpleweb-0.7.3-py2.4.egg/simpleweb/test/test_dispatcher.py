import dispatcher

def GET():
	return "GET"
	pass

class TestUrls(object):

	def test_add(self):
		urls = dispatcher.Urls()
		urls.add('/', 'test_dispatcher')
		urls.add('/foo', 'foo.bar.noexist')

		assert ('/', 'test_dispatcher') in urls.urlmap
		assert ('/foo', 'foo.bar.noexist') in urls.urlmap

	def test_geturls(self):
		urls = dispatcher.Urls()
		urls.add('/', 'test_dispatcher')
		myurls = urls.geturls()
		print myurls.mappings
		assert myurls.mappings[0][1]['GET']

