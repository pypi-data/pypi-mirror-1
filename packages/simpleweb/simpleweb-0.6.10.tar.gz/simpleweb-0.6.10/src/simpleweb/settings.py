import sys

class Config(object):
	"""
	Grabs config.py information and makes it and any other information available conveniently
	"""

	def __init__(self, conf_file='config'):
		sys.path.insert(0, '.')
		module = __import__(conf_file)
		var_list = (v for v in dir(module)) # if not v.startswith('__'))
		for attr in var_list:
			setattr(self, attr, getattr(module, attr))
