import sys
import simpleweb

def help(name, args):
	if len(args) < 1:
		print "Usage: simpleweb-admin [command]"
		print
		print "Available Commands:"
		try:
			plugins = __import__('simpleweb.admin.plugins', {}, {}, 'plugins')
		except ImportError, e:
			simpleweb.utils.msg_err("Failed to import simpleweb.admin.plugins: %s" % (e))
			sys.exit()
		else:
			for i in plugins.__all__:
				print "  %s" % (i.replace('_', '-'))
			print "  help"
			print "  help [command]"

	if len(args) == 1:
		command = args[0]
		try:
			module = __import__('simpleweb.admin.plugins.%s' % (command), {}, {}, command)
		except ImportError:
			simpleweb.utils.msg_err("Command '%s' is not implemented" % (command))
		else:
			sys.stdout.write("%s\n" % (getattr(module, command).__doc__))
