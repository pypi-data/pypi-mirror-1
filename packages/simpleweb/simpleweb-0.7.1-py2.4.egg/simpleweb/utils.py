import sys

ENV_KEY_FLUP_SESSION='com.saddi.service.session'
ENV_KEY_AUTH_MIDDLEWARE='simpleweb.middleware.auth.user'

def doctor_system_path(sys):
	sys.path.insert(0, '.')

def from_import(m, try_class=True):
	"""
	Given a module string 'a.b.c' will do:

	from a.b import c and return c to the caller
	"""
	#if string is 'a', we just 'import a'
	if m.find('.') < 0:
		return __import__(m)
	else:
		#now the string is definitely 'a.b[.c[.d]]' and so on
		package, module = m.rsplit('.', 1)

		#try to do from package import module
		try:
			r = __import__(m, {}, {}, [module])
		except ImportError, e:
			#if import fails, we'll believe its a class
			#and then try to back up the import path, and
			#import the module there, and get the class as an
			#attribute of the module. All this only if 'try_class' is 
			# True
			if not try_class:
				sys.stderr.write("Failed to import '%s'. Details Below:\n\t%s\n" % (m, e))
				sys.exit(1)
			else:
				_module = from_import(package, try_class=False)
				try:
					return getattr(_module, module) #if the previous works, then module is a class in _module
				except AttributeError:
					sys.stderr.write("Failed to import '%s'. '%s' not found in '%s'\n" % (m, module, package))
					sys.exit(1)
		else: 
			#if the import succeeds, return the module
			return r

def get_functions(m):
	"""
	Given a module 'm', will return a generator of
	all the function objects in the module. Given a class,
	will return a generator of all the actual functions
	attached to the methods of the class.
	"""
	m = from_import(m)
	objs = vars(m)

	for fn in objs.values():
		if hasattr(fn, 'func_name'):
			yield fn
		elif hasattr(fn, 'im_func'):
			yield fn.im_func


def get_methods_dict(m, list_of_methods):
	"""
	Given a module/class object m and a list of methods ['A', 'B', 'func']
	will return a dict like: {'A':m.A, 'B':m.B, 'func':m.func}.

	If any of m.A, m.B or m.func doesn't exist, the dictionary won't include it
	"""
	funcs = get_functions(m)
	method_dict = {}
	for f in funcs:
		if f.func_name in list_of_methods:
			method_dict[f.func_name] = f

	return method_dict
