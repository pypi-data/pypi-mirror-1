ENV_KEY_FLUP_SESSION='com.saddi.service.session'
ENV_KEY_AUTH_MIDDLEWARE='simpleweb.middleware.auth.user'

def doctor_system_path(sys):
	import sys
	sys.path.insert(0, '.')

def from_import(m):
	"""
	Given a module string 'a.b.c' will do:

	from a.b import c and return c to the caller
	"""
	try:
		p, module = m.rsplit('.', 1)
	except ValueError:
		print "setting module to empty string"
		module = ""

	r = __import__(m, {}, {}, [module])

	return r

def get_functions(m):
	"""
	Given a module 'm', will return a generator of
	all the function objects in the module.
	"""
	m = from_import(m)
	objs = vars(m)
	return (fn for fn in objs.values() if hasattr(fn, 'func_name'))


def get_methods_dict(m, list_of_methods):
	"""
	Given a module object m and a list of methods ['A', 'B', 'func']
	will return a dict like: {'A':m.A, 'B':m.B, 'func':m.func}.

	If any of m.A, m.B or m.func doesn't exist, the dictionary won't include it
	"""
	funcs = get_functions(m)
	method_dict = {}
	for f in funcs:
		if f.func_name in list_of_methods:
			method_dict[f.func_name] = f

	return method_dict


