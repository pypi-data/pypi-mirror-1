import sys
import simpleweb.utils

#TODO: refactor create_tables, drop_tables, etc, as closures.
def drop_tables(name, args):
	"""Usage: simpleweb-admin droptables

Drop all the tables defined in the models for a simpleweb project.
config.db_plugin has to be configured first.
"""
	if len(args) > 0:
		simpleweb.utils.msg_err("command '%s' takes no arguments" %(name))
		sys.exit(0)

	try:
		sys.path.insert(0, '.')
		config = __import__('config')
		config.db_plugin.droptables()
	except ImportError, e:
		simpleweb.utils.msg_err("Could not successfully import config.py: %s" % (e))
	except AttributeError:
		simpleweb.utils.msg_err("No db_plugin has been setup in config.py. Please do so first")

