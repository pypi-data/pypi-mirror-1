import sys

_modules = []
_new_modules = []

def register():
	global _modules, _new_modules
	_modules = sys.modules.keys()
	_new_modules = []

def _import(modpath, globals, locals, module):
	global _modules, _new_modules
	for m in _new_modules:
		if m not in _modules:
			print "removing %s..." %(m)
			sys.modules.pop(m)
	module = __import__(modpath, {}, {}, module)
	_new_modules = sys.modules.keys()

	return module

register()

def get_func(path):
	''' take a path like path.to.module:func and return the func'''
	modpath, funcname = path.split(':', 2)
	#modpath = seplist[0]
	#funcname = seplist[1]
	modslist = modpath.split('.')
	modchild = modslist[len(modslist) - 1]
	module = _import(modpath, {}, {}, modchild)
	return getattr(module, funcname)


