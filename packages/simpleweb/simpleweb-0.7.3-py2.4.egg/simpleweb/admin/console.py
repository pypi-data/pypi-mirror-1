import sys
import os
import simpleweb.utils

def main():
	command = "run"
	name = os.path.basename(sys.argv[0])
	del sys.argv[0] 
	try:
		command = sys.argv[0]
		command = command.replace('-', '_')
		del sys.argv[0]
	except IndexError:
		pass

	args = sys.argv


	try:
		module = __import__('simpleweb.admin.plugins.' + command, {}, {}, command)
		func = vars(module)[command]
		name = "%s %s" % (name, command)
	except ImportError, e:
		simpleweb.utils.msg_err("Error loading the plugin : %s" % (e))
		return
	except KeyError, e:
		simpleweb.utils.msg_err("Function %s is not defined in plugin module %s" % (command, command))
		return

	func(name, args)


