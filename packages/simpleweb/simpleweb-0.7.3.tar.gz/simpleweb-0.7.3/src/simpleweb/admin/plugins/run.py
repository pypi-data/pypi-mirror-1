import sys
import simpleweb

def run(name, args):
	"""Usage: simpleweb-admin run 

Start the simpleweb application in the current directory, 
in the internal development web server
	"""

	if len(args) > 0:
		simpleweb.utils.msg_err("'%s' takes no arguments" % (name))
		sys.exit(0)

	simpleweb.run()
