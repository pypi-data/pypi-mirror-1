import dispatcher

__urlmap = dispatcher.Urls()

def urladd(url, controller):
	__urlmap.add(url, controller)

def geturls():
	return __urlmap.geturls()
