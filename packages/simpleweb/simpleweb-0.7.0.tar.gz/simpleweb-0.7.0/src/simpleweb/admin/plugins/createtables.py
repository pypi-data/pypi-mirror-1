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
	except ImportError, e:
		sys.stderr.write("Could not successfully import config.py. Details follow:\n\t%s\n" % (e))
