import sys
import os

def main():
	command = "run"
	name = os.path.basename(sys.argv[0])
	del sys.argv[0] 
	try:
		command = sys.argv[0]
		del sys.argv[0]
	except IndexError:
		pass

	args = sys.argv


	try:
		module = __import__('simpleweb.admin.plugins.' + command, {}, {}, command)
		func = vars(module)[command]
		name = "%s %s" % (name, command)
	except ImportError, e:
		return "Error loading the <%s> plugin :\n\t%s\n" % (command, e)
	except KeyError, e:
		return "Function %s is not defined in plugin module %s\n" % (command, command)

	func(name, args)


