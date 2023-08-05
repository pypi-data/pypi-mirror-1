#trivial internal static page server for development ONLY

def GET(request, page):
	return "serving %s" % (page)
