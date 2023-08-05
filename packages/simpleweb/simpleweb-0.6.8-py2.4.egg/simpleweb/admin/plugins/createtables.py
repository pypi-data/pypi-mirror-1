import sys

def createtables(name, args):
	"""Usage: simpleweb-admin createtables

Create all the tables defined in the models for a simpleweb project.
config.db_plugin has to be configured first.
"""
	if len(args) > 0:
		sys.stderr.write("command 'createtables' takes no arguments\n")
		sys.exit(0)

	try:
		sys.path.insert(0, '.')
		config = __import__('config')
		config.db_plugin.createtables()
	except ImportError:
		sys.stderr.write("Can not find config.py. Is this a valid simpleweb project directory?\n")
