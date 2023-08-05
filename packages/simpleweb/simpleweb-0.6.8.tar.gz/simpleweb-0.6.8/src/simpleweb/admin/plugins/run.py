import sys
import simpleweb

def run(name, args):
	"""Usage: simpleweb-admin run 

Start the simpleweb application in the current directory, 
in the internal development web server
	"""

	if len(args) > 0:
		sys.stderr.write("RUN takes no arguments\n")
		sys.exit(0)

	try:
		sys.path.insert(0, '.')
		__import__('urls')
	except ImportError:
		sys.stderr.write("Cannot find valid urls.py. Is this a simpleweb project directory?\n")
	else:
		simpleweb.run()
	
	

