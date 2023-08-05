import os
from simpleweb.admin.plugins import deploy
import test_deploy

def test_is_in_current_app():
	class dummy:
		__doc__ = 'A dummy object to pass the is_current_app criteria'
		__file__ = './foo/bar.py'
		pass

	amodule = dummy()
	print amodule.__file__
	assert deploy.is_in_current_app(amodule) is True


def test_is_package():
	import simpleweb
	assert deploy.is_package('simpleweb', simpleweb) is True

	import os.path
	assert deploy.is_package('os.path', os.path) is False

def test_build_pkg_path():
	assert deploy.build_pkg_path('a.b.c') == 'a/b/c'

def test_is_nested_module():
	import simpleweb.webserver
	assert deploy.is_nested_module('simpleweb.webserver', simpleweb.webserver) is True

	import email
	assert deploy.is_nested_module('email', email) is False

def test_build_nested_module_path():
	assert deploy.build_nested_module_path('a.b.c') == 'a/b'

def test_get_module_file():
	import test_deploy
	test_deploy_filename = deploy.get_module_file(test_deploy)
	test_deploy_file = open(test_deploy_filename, 'r')
	test_deploy_contents = test_deploy_file.read()
	test_deploy_file.close()

	this_file = open(__file__, 'r')
	this_contents = this_file.read()
	this_file.close()

	assert test_deploy_contents == this_contents

def test_create_pkg_dir():
	root_dir = 'root_dir'
	path1 = deploy.create_pkg_dir('a.b.c', root_dir=root_dir, dummy_run=True)
	assert path1 == os.path.join(root_dir, 'a', 'b', 'c')

	path2 = deploy.create_pkg_dir('a.b.c', root_dir=root_dir, is_pkg=False, dummy_run=True)
	assert path2 == os.path.join(root_dir, 'a', 'b')
