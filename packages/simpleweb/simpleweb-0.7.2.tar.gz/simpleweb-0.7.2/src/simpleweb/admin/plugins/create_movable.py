import sys
import os
import shutil
import distutils.sysconfig

try:
	import pkg_resources
except ImportError:
	simpleweb.utils.optional_dependency_err('Standalone Deployment', 'setuptools')

def create_movable(name, args):
	'''Usage: simpleweb-admin movable [lib-folder]

The movable option is used to aid in easy deployment of simpleweb applications.
Using this option, all the modules used for the application are packaged into 
a single folder which is then added to sys.path, using a custom sitecustomize.py

This helps in deployments that are supposed to be contained, for instance
Shared Web Hosts.
'''
	#create the library directory
	lib_dir = 'site-packages'
	try:
		lib_dir = args[0]
	except IndexError:
		#ignore and use 'site-package' as lib_dir
		pass

	lib_dir = os.path.join(os.getcwd(), lib_dir)
	try:
		os.mkdir(lib_dir)
	except OSError, (code, msg):
		if code == 17: #File Exists.
			#delete it first
			rm_sitecustomize(os.getcwd(), lib_dir)
			shutil.rmtree(lib_dir)
			pass
		else:
			raise

	#create a SimplewebApp()
	from simpleweb.app import SimplewebApp
	import simpleweb._urls as urls
	from simpleweb.settings import Config

	app = SimplewebApp(urls, Config("config"))


	#now build a list of all the actual module files
	#we're using since we created the app
	for name, module in sys.modules.items():
		#some modules are usually imported into other modules
		#for instance, in simpleweb, if you import sys
		#NAME: will show up as simpleweb.sys, but MODULE: will be None
		#in sys.modules. We ignore these.
		if module and hasattr(module, '__file__'):
			dest_path = lib_dir

			if is_filtered(lib_dir, name, module):
				continue

			if is_package(name, module):
				dest_path = create_pkg_dir(name, root_dir=dest_path)
			elif is_nested_module(name, module):
				dest_path = create_pkg_dir(name, root_dir=dest_path, is_pkg=False)

			src_path = get_module_file(module)
			copy_module_file(src_path, dest_path)

	create_sitecustomize(os.getcwd(), lib_dir)

def rm_sitecustomize(root_dir, lib_dir):
	try:
		dest_path = os.path.join(root_dir, 'sitecustomize.py')
		os.unlink(dest_path)

		dest_path = os.path.join(root_dir, 'sitecustomize.pyc')
		os.unlink(dest_path)

		dest_path = os.path.join(root_dir, 'sitecustomize.pyo')
		os.unlink(dest_path)
	except OSError, (code, msg):
		if code == 2: #No such file or directory
			#ignore
			pass

def create_sitecustomize(root_dir, lib_dir):
	sitecustomize_py = '''
import sys
import os

libdir = '%s'
path = os.path.join(os.getcwd(), libdir)
sys.path.append(path)

if __name__ == '__main__':
	print path, "will be added to sys.path"
''' % (lib_dir)

	dest_path = os.path.join(root_dir, 'sitecustomize.py')
	f = open(dest_path, 'w')
	f.write(sitecustomize_py)
	f.close()
	
def create_pkg_dir(pkgname, root_dir, is_pkg=True, dummy_run=False):
	if is_pkg:
		rel_path = build_pkg_path(pkgname)
	else:
		rel_path = build_nested_module_path(pkgname)

	path = os.path.join(root_dir, rel_path)

	if not dummy_run:
		try:
			os.makedirs(path)
		except OSError, (code, msg):
			if code == 17:
				#ignore, File Exists
				pass
			else:
				raise
	return path

def is_package(modulename, module):
	filename = os.path.split(module.__file__)[1]
	if filename.startswith('__init__.py'):
		return True
	else:
		return False

def is_nested_module(modulename, module):
	if modulename.find('.') >= 0:
		return True
	else:
		return False

def build_pkg_path(pkgname):
	#if we have 'a.b.c' as the actual package,
	#then we should have a/b/c
	#so that we'll eventually have a/b/c/__init__.py
	path = pkgname
	return path.replace('.', os.path.sep)

def build_nested_module_path(pkgname):
	#if we have a.b.c, c as the actual module
	#we need to to return a/b not a/b/c
	#so that our result will be:
	# a/b/cmodule.py NOT a/b/c/cmodule.py

	path = pkgname[:pkgname.rfind('.')]
	return path.replace('.', os.path.sep)


def get_module_file(module):
	module_file_path, module_file  = os.path.split(module.__file__)
	ext = os.path.splitext(module_file)[1]
	if ext == '.pyc':
		module_file = module_file.replace('.pyc', '.py')

	if ext == '.pyo':
		module_file = module_file.replace('.pyo', '.py')

	src_path = pkg_resources.resource_filename(module.__name__, module_file)
	return src_path

def copy_module_file(src_path, dst_path):
	shutil.copy(src_path, dst_path)


#Filters
def is_filtered(lib_dir, name, module):
	if is_stdlib(module):
		return True
	elif is_in_libdir(lib_dir, module):
		return True
	elif is_in_current_app(module):
		return True
	else:
		return False

def is_stdlib(module):
	site_packages_prefix = distutils.sysconfig.get_python_lib()
	stdlib_prefix = os.path.split(site_packages_prefix)[0]
	if not module.__file__.startswith(site_packages_prefix) and module.__file__.startswith(stdlib_prefix):
		return True
	else:
		return False

def is_in_libdir(lib_dir, module):
	if module.__file__.startswith(lib_dir):
		return True
	else:
		return False

def is_in_current_app(module):
	#file path starts with ./path/to/file or file is local sitecustomize.py
	if module.__file__.startswith('.') or os.path.split(module.__file__)[1].startswith('sitecustomize'):
		return True
	else:
		return False

def is_simpleweb_module(name):
	if name.startswith('simpleweb'):
		return True
	else:
		return False
