import sys

class Config(object):
	"""
	Grabs config.py information and makes it and any other information available conveniently
	"""

	def __init__(self, conf_file='config'):
		sys.path.insert(0, '.')
		try:
			module = __import__(conf_file)
		except ImportError, e:
			sys.stderr.write("Could not successfully import config.py. Details Below:\n\t%s\n" % (e))
			sys.exit(1)
		else:
			var_list = (v for v in dir(module)) # if not v.startswith('__'))
			for attr in var_list:
				setattr(self, attr, getattr(module, attr))
