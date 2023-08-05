import sys
import os
import string

import templates

def createproject(cmdline, args):
	"""Usage: simpleweb-admin createproject <project-name> [summary] [description string]

Creates a new simpleweb project Project-Name. The new project
will have the neccessary files and filesystem structure that
a simpleweb project requires.
	"""

	if len(args) < 1 or len(args) > 3: 
		sys.stderr.write("Try simpleweb-admin help createproject for help\n")
		sys.exit()

	summary = ""
	description = ""	
	try:
		projectname = args[0]
		summary = args[1]
		description = args[2]
	except IndexError:
		pass

	create_folder_toplevel(projectname, summary, description)
	create_file(projectname, 'main.py', templates.main_py, 0755)
	create_file(projectname, 'config.py', templates.config_py)
	create_file(projectname, 'urls.py', templates.urls_py)
	create_file(projectname, 'models.py', templates.models_py)
	create_folder(projectname, 'static', subfolders=['css', 'img', 'js'])
	create_file(projectname, 'static/css/main.css', templates.main_css)
	create_folder(projectname, 'templates')
	create_file(projectname, 'templates/index.html', templates.index_html)
	create_file(projectname, 'templates/master.html', templates.master_html)
	create_folder(projectname, 'tests')
	controllers_project = "%s/%s" % (projectname, 'controllers')
	create_folder_toplevel(controllers_project, "The controllers package for %s" % (projectname), "This package contains standalone controllers for the project %s" % (projectname))
	create_file(projectname, 'controllers/index.py', templates.index_py)

def create_folder_toplevel(projectname, summary="", description=""):
	try:
		os.mkdir(projectname)
		f = open("%s/__init__.py" % (projectname), 'w')
		#TODO: apply line wrap to 'description' so it looks good in pydoc
		f.write('"""\n%s\n\n%s\n"""' % (summary, description))
		f.close()
	except Exception, e:
		sys.stderr.write("Error creating toplevel:\n\t%s\n" % (e))

def create_folder(projectname, foldername, subfolders=[]):
	try:
		fname = "%s/%s" % (projectname, foldername)
		os.mkdir(fname)
		for f in subfolders:
			create_folder(fname, f)
	except Exception, e:
		sys.stderr.write("Error creating folder: \n\t%s\n" % (e))

def create_file(projectname, filename, template_string, perms=0644):
	try:
		fname = "%s/%s" % (projectname, filename)
		f = open(fname, 'w')
		content = string.Template(template_string)
		#TODO: pass in a dict() of 'templatekey=realvalue' pairs
		# so we're more flexible
		f.write(content.substitute(projectname=projectname))
		f.close()
		os.chmod(f, perms)
	except Exception, e:
		sys.stderr.write("Error creating file:\n\t%s\n" %(e))
