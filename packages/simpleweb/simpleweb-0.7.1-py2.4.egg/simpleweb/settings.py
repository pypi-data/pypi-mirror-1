import os
import sys
import simpleweb.utils

class Config(object):
	"""
	Grabs config.py information and makes it and any other 
	information available conveniently for internal use.
	"""

	def __init__(self, conf_file='config'):
		sys.path.insert(0, '.')
		try:
			module = __import__(conf_file)
			self.working_directory = os.getcwd()
		except ImportError, e:
			sys.stderr.write("Could not successfully import config.py. Details Below:\n\t%s\n" % (e))
			sys.exit(1)
		else:
			var_list = (v for v in dir(module) if not v.startswith('__'))
			for attr in var_list:
				setattr(self, attr, getattr(module, attr))

		self.set_default_attr('enable_debug', False)
		self.set_default_attr('enable_sessions', False)
		self.set_default_attr('server_port', 8080)
		self.set_default_attr('server_host', '127.0.0.1')
		self.set_default_attr('server_reload', True)
		self.set_default_attr('server_user', 'nobody')
		self.set_default_attr('server_group', 'nobody')

	def set_default_attr(self, key, value):
		if not hasattr(self, key) or str(getattr(self, key)).strip() == '' or getattr(self, key) is None:
			setattr(self, key, value)
