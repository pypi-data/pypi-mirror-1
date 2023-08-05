import sys
import simpleweb.utils

def createtables(name, args):
	"""Usage: simpleweb-admin createtables

Create all the tables defined in the models for a simpleweb project.
config.db_plugin has to be configured first.
"""
	if len(args) > 0:
		simpleweb.utils.msg_err("command 'createtables' takes no arguments")
		sys.exit(0)

	try:
		sys.path.insert(0, '.')
		config = __import__('config')
		config.db_plugin.createtables()
	except ImportError, e:
		simpleweb.utils.msg_err("Could not successfully import config.py: %s" % (e))
